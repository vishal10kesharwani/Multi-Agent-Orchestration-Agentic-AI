/**
 * Dashboard JavaScript for Multi-Agent Orchestration Platform
 */

class Dashboard {
    constructor() {
        this.apiBase = '/api/v1';
        this.refreshInterval = 5000; // 5 seconds
        this.chart = null;
        this.systemData = {};
        this.performanceChart = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.initializePerformanceChart();
        await this.loadDashboardData();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Task form submission
        document.getElementById('taskForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitTask();
        });

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
                this.loadDashboardData().finally(() => {
                    refreshBtn.disabled = false;
                    refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
                });
            });
        }

        // Quick action buttons
        const generateReportBtn = document.getElementById('generateReportBtn');
        if (generateReportBtn) {
            generateReportBtn.addEventListener('click', this.generateSystemReport);
        }
    }

    startAutoRefresh() {
        // Refresh every 5 seconds
        setInterval(() => {
            this.loadDashboardData();
        }, this.refreshInterval);
    }

    async loadDashboardData() {
        try {
            await Promise.all([
                this.updateSystemStatus(),
                this.updateTasksList(),
                this.updateAgentsList()
            ]);
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            this.showToast('Error loading dashboard data', 'error');
        }
    }

    async updateSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/system/status`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.systemData = await response.json();
            
            // Update system overview widgets
            this.updateElement('activeTasks', this.systemData.active_tasks || 0);
            this.updateElement('totalAgents', this.systemData.total_agents || 0);
            this.updateElement('systemLoad', `${this.systemData.system_load || 0}%`);
            this.updateElement('messageRate', `${this.systemData.message_rate || 0}`);
            
            // Update system status panel
            this.updateElement('systemStatus', this.systemData.status || 'Unknown');
            this.updateElement('systemUptime', this.systemData.uptime || 'Unknown');
            this.updateElement('systemVersion', this.systemData.version || '1.0.0');
            
            // Update performance chart
            await this.updatePerformanceChart();
            
            // Update status indicators
            const statusElement = document.getElementById('systemStatus');
            if (statusElement) {
                statusElement.className = this.systemData.status === 'online' ? 'status-online' : 'status-offline';
            }
            
            // Update AI API status warning
            this.updateAIApiWarning();
            
        } catch (error) {
            console.error('Error updating system status:', error);
            this.updateElement('systemStatus', 'Error');
        }
    }

    async updateTasksList() {
        try {
            const response = await fetch(`${this.apiBase}/tasks?limit=10`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            const tasksList = document.getElementById('tasksList');
            
            if (!tasksList) return;
            
            if (!data.tasks || data.tasks.length === 0) {
                tasksList.innerHTML = '<div class="no-data">No recent tasks</div>';
                return;
            }
            
            tasksList.innerHTML = data.tasks.map(task => `
                <div class="task-item ${task.status}" onclick="window.showTaskDetails(${task.id})">
                    <div class="task-header">
                        <span class="task-title">${this.escapeHtml(task.title)}</span>
                        <span class="task-status status-${task.status}">
                            ${this.getStatusIcon(task.status)} ${task.status}
                        </span>
                    </div>
                    <div class="task-meta">
                        <span class="task-priority">Priority: ${task.priority}</span>
                        <span class="task-progress">${Math.round((task.progress || 0) * 100)}%</span>
                        ${task.assigned_agent_id ? `<span class="task-agent">Agent ${task.assigned_agent_id}</span>` : ''}
                    </div>
                    <div class="task-description">${this.escapeHtml(task.description?.substring(0, 100) || '')}${task.description?.length > 100 ? '...' : ''}</div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error updating tasks list:', error);
            const tasksList = document.getElementById('tasksList');
            if (tasksList) {
                tasksList.innerHTML = '<div class="error">Error loading tasks</div>';
            }
        }
    }

    async updateAgentsList() {
        try {
            const response = await fetch(`${this.apiBase}/agents`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            const agentsList = document.getElementById('agentsList');
            
            if (!agentsList) return;
            
            if (!data.agents || data.agents.length === 0) {
                agentsList.innerHTML = '<div class="no-data">No agents available</div>';
                return;
            }
            
            agentsList.innerHTML = data.agents.map(agent => `
                <div class="agent-item ${agent.status}">
                    <div class="agent-header">
                        <span class="agent-name">${this.escapeHtml(agent.name)}</span>
                        <span class="agent-status status-${agent.status}">
                            ${this.getAgentStatusIcon(agent.status)} ${agent.status}
                        </span>
                    </div>
                    <div class="agent-capabilities">
                        ${(agent.capabilities || []).map(cap => 
                            `<span class="capability-tag">${this.escapeHtml(cap)}</span>`
                        ).join('')}
                    </div>
                    <div class="agent-description">${this.escapeHtml(agent.description || '')}</div>
                </div>
            `).join('');
            
        } catch (error) {
            console.error('Error updating agents list:', error);
            const agentsList = document.getElementById('agentsList');
            if (agentsList) {
                agentsList.innerHTML = '<div class="error">Error loading agents</div>';
            }
        }
    }

    getStatusIcon(status) {
        const icons = {
            'pending': '<i class="fas fa-clock text-warning"></i>',
            'in_progress': '<i class="fas fa-spinner fa-spin text-info"></i>',
            'completed': '<i class="fas fa-check-circle text-success"></i>',
            'failed': '<i class="fas fa-times-circle text-danger"></i>'
        };
        return icons[status] || '<i class="fas fa-question-circle"></i>';
    }

    getAgentStatusIcon(status) {
        const icons = {
            'idle': '<i class="fas fa-circle text-success"></i>',
            'busy': '<i class="fas fa-spinner fa-spin text-warning"></i>',
            'offline': '<i class="fas fa-circle text-danger"></i>'
        };
        return icons[status] || '<i class="fas fa-question-circle"></i>';
    }

    async showTaskDetails(taskId) {
        try {
            const [taskResponse, agentsResponse] = await Promise.all([
                fetch(`${this.apiBase}/tasks/${taskId}`),
                fetch(`${this.apiBase}/agents`)
            ]);
            
            if (!taskResponse.ok) throw new Error(`HTTP ${taskResponse.status}`);
            
            const task = await taskResponse.json();
            const agentsData = agentsResponse.ok ? await agentsResponse.json() : { agents: [] };
            
            // Find assigned agent details
            const assignedAgent = task.assigned_agent_id ? 
                agentsData.agents.find(agent => agent.id === task.assigned_agent_id) : null;
            
            // Create modal content
            const modalContent = `
                <div class="task-detail-modal">
                    <div class="modal-header">
                        <h3>${this.escapeHtml(task.title)}</h3>
                        <span class="task-status status-${task.status}">
                            ${this.getStatusIcon(task.status)} ${task.status}
                        </span>
                    </div>
                    
                    <div class="modal-body">
                        <div class="task-info">
                            <div class="info-row">
                                <strong>Description:</strong>
                                <p>${this.escapeHtml(task.description)}</p>
                            </div>
                            
                            <div class="info-row">
                                <strong>Priority:</strong> 
                                <span class="priority-${task.priority}">${task.priority}</span>
                            </div>
                            
                            <div class="info-row">
                                <strong>Progress:</strong> 
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${Math.round((task.progress || 0) * 100)}%"></div>
                                    <span class="progress-text">${Math.round((task.progress || 0) * 100)}%</span>
                                </div>
                            </div>
                            
                            ${assignedAgent ? `
                                <div class="info-row">
                                    <strong>Assigned Agent:</strong> 
                                    <div class="agent-info">
                                        <span class="agent-name">${this.escapeHtml(assignedAgent.name)}</span>
                                        <span class="agent-status status-${assignedAgent.status}">${assignedAgent.status}</span>
                                        <div class="agent-capabilities">
                                            ${(assignedAgent.capabilities || []).map(cap => 
                                                `<span class="capability-tag">${this.escapeHtml(cap)}</span>`
                                            ).join('')}
                                        </div>
                                    </div>
                                </div>
                            ` : task.assigned_agent_id ? `
                                <div class="info-row">
                                    <strong>Assigned Agent:</strong> Agent ${task.assigned_agent_id}
                                </div>
                            ` : ''}
                            
                            <div class="info-row">
                                <strong>Created:</strong> ${this.formatDateTime(task.created_at)}
                            </div>
                            
                            ${task.completed_at ? `
                                <div class="info-row">
                                    <strong>Completed:</strong> ${this.formatDateTime(task.completed_at)}
                                </div>
                            ` : ''}
                        </div>
                        
                        ${task.ai_response ? `
                            <div class="ai-response-section">
                                <h4><i class="fas fa-robot"></i> AI Agent Response</h4>
                                ${assignedAgent ? `
                                    <div class="response-agent-info">
                                        <strong>Response from:</strong> ${this.escapeHtml(assignedAgent.name)}
                                        <span class="agent-type">(${assignedAgent.capabilities ? assignedAgent.capabilities.join(', ') : 'Multi-purpose'} Agent)</span>
                                    </div>
                                ` : ''}
                                <div class="ai-response-content">
                                    <div class="response-header">
                                        <i class="fas fa-comment-dots"></i> <strong>Task Solution:</strong>
                                    </div>
                                    <div class="response-text">
                                        ${this.formatAIResponse(task.ai_response)}
                                    </div>
                                </div>
                            </div>
                        ` : task.status === 'completed' ? `
                            <div class="ai-response-section">
                                <h4><i class="fas fa-robot"></i> AI Agent Response</h4>
                                <div class="no-response">
                                    <i class="fas fa-info-circle"></i>
                                    Task completed but no AI response recorded.
                                </div>
                            </div>
                        ` : task.status === 'in_progress' ? `
                            <div class="ai-response-section">
                                <h4><i class="fas fa-robot"></i> AI Agent Response</h4>
                                <div class="pending-response">
                                    <i class="fas fa-spinner fa-spin"></i>
                                    AI agent is working on this task...
                                </div>
                            </div>
                        ` : ''}
                        
                        ${task.execution_details && task.execution_details.length > 0 ? `
                            <div class="execution-details-section">
                                <h4><i class="fas fa-list"></i> Execution Details</h4>
                                <div class="execution-timeline">
                                    ${task.execution_details.map(detail => `
                                        <div class="timeline-item">
                                            <div class="timeline-time">${this.formatDateTime(detail.timestamp)}</div>
                                            <div class="timeline-content">
                                                <strong>${detail.action}</strong>
                                                <span class="status-${detail.status}">${detail.status}</span>
                                                ${detail.details ? `<p>${this.escapeHtml(detail.details)}</p>` : ''}
                                            </div>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    
                    <div class="modal-footer">
                        <button onclick="window.dashboard.closeModal()" class="btn btn-secondary">Close</button>
                    </div>
                </div>
            `;
            
            this.showModal(modalContent);
            
        } catch (error) {
            console.error('Error loading task details:', error);
            this.showToast('Error loading task details', 'error');
        }
    }

    showModal(content) {
        // Remove existing modal
        const existingModal = document.getElementById('taskModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Create modal
        const modal = document.createElement('div');
        modal.id = 'taskModal';
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-container">
                ${content}
            </div>
        `;
        
        // Add to page
        document.body.appendChild(modal);
        
        // Add click outside to close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeModal();
            }
        });
        
        // Add escape key to close
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeModal();
            }
        });
    }

    closeModal() {
        const modal = document.getElementById('taskModal');
        if (modal) {
            modal.remove();
        }
    }

    initializePerformanceChart() {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'System Load (%)',
                    data: [],
                    borderColor: 'rgb(59, 130, 246)',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }, {
                    label: 'Active Tasks',
                    data: [],
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        max: 100,
                        title: {
                            display: true,
                            text: 'System Load (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Active Tasks'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    async updatePerformanceChart() {
        try {
            const response = await fetch(`${this.apiBase}/system/status`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();

            const now = new Date();
            const timeLabel = now.toLocaleTimeString();

            // Add new data point
            this.performanceChart.data.labels.push(timeLabel);
            this.performanceChart.data.datasets[0].data.push(data.system_load || 0);
            this.performanceChart.data.datasets[1].data.push(data.active_tasks || 0);

            // Keep only last 10 data points
            if (this.performanceChart.data.labels.length > 10) {
                this.performanceChart.data.labels.shift();
                this.performanceChart.data.datasets[0].data.shift();
                this.performanceChart.data.datasets[1].data.shift();
            }

            this.performanceChart.update('none');

        } catch (error) {
            console.error('Error updating performance chart:', error);
        }
    }

    async submitTask() {
        const title = document.getElementById('taskTitle').value.trim();
        const description = document.getElementById('taskDescription').value.trim();
        const priority = document.getElementById('taskPriority').value;
        const capabilitiesSelect = document.getElementById('taskCapabilities');
        const capabilities = Array.from(capabilitiesSelect.selectedOptions).map(option => option.value);

        if (!title || !description) {
            this.showToast('Please fill in all required fields', 'error');
            return;
        }

        const taskData = {
            title,
            description,
            priority: priority || 'medium',
            requirements: {
                capabilities: capabilities,
                complexity: capabilities.length > 2 ? 'high' : 'medium'
            },
            input_data: {}
        };

        try {
            const response = await fetch(`${this.apiBase}/tasks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(taskData)
            });

            if (response.ok) {
                const result = await response.json();
                if (result.success) {
                    this.showToast(`Task submitted successfully! ID: ${result.task_id}`, 'success');
                    document.getElementById('taskForm').reset();
                    await this.updateTasksList();
                    await this.updateSystemStatus();
                } else {
                    this.showToast(`Failed to submit task: ${result.error || 'Unknown error'}`, 'error');
                }
            } else {
                const errorText = await response.text();
                this.showToast(`HTTP Error ${response.status}: ${errorText}`, 'error');
            }
        } catch (error) {
            console.error('Error submitting task:', error);
            this.showToast('Error submitting task: ' + error.message, 'error');
        }
    }

    updateCapabilitiesDisplay() {
        const select = document.getElementById('taskCapabilities');
        const selected = Array.from(select.selectedOptions).map(option => option.text);
        
        // You could add a display element to show selected capabilities
        // For now, we'll just ensure the multi-select works properly
    }

    updateConnectionStatus(connected) {
        const statusDiv = document.getElementById('connectionStatus');
        const indicator = statusDiv.querySelector('.status-indicator');
        const text = statusDiv.querySelector('span');

        if (connected) {
            indicator.className = 'status-indicator status-idle';
            text.textContent = 'Connected';
        } else {
            indicator.className = 'status-indicator status-error';
            text.textContent = 'Disconnected';
        }
    }

    showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const bgColors = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        };

        toast.className = `${bgColors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);

        // Remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 5000);
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value != null ? String(value) : '';
        }
    }

    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString();
    }

    updateAIApiWarning() {
        const warningContainer = document.getElementById('aiApiWarning');
        const messageElement = document.getElementById('aiApiMessage');
        
        if (this.systemData.ai_api_status === 'restricted' || this.systemData.ai_api_status === 'error') {
            if (warningContainer) {
                warningContainer.style.display = 'block';
            }
            if (messageElement && this.systemData.ai_api_message) {
                messageElement.textContent = this.systemData.ai_api_message;
            }
        } else {
            if (warningContainer) {
                warningContainer.style.display = 'none';
            }
        }
    }

    formatAIResponse(response) {
        if (!response) return '';
        
        // Convert to string if it's an object
        let text = typeof response === 'object' ? JSON.stringify(response, null, 2) : String(response);
        
        // Basic formatting for better readability
        text = text.replace(/\n/g, '<br>');
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold **text**
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic *text*
        text = text.replace(/`(.*?)`/g, '<code>$1</code>'); // Code `text`
        
        return text;
    }
}

// Global functions for quick actions
async function runTestScenario() {
    try {
        dashboard.showToast('Running test scenario...', 'info');
        
        // Submit a test task
        const testTask = {
            title: 'Test Scenario - Data Analysis',
            description: 'Automated test scenario for platform validation',
            priority: 'medium',
            requirements: {
                capabilities: ['data_analysis']
            },
            input_data: {
                test_mode: true,
                scenario: 'automated_test'
            }
        };

        const response = await fetch('/api/v1/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(testTask)
        });

        const result = await response.json();
        
        if (result.success) {
            dashboard.showToast(`Test scenario started! Task ID: ${result.task_id}`, 'success');
        } else {
            dashboard.showToast('Failed to start test scenario', 'error');
        }
    } catch (error) {
        console.error('Error running test scenario:', error);
        dashboard.showToast('Error running test scenario', 'error');
    }
}

async function generateReport() {
    try {
        dashboard.showToast('Generating performance report...', 'info');
        
        const response = await fetch('/api/v1/monitoring/performance');
        if (response.ok) {
            const report = await response.json();
            dashboard.showToast('Performance report generated successfully!', 'success');
            console.log('Performance Report:', report);
        } else {
            dashboard.showToast(`Failed to generate report (HTTP ${response.status})`, 'error');
        }
    } catch (error) {
        console.error('Error generating report:', error);
        dashboard.showToast('Error generating report', 'error');
    }
}

async function rebalanceLoad() {
    try {
        dashboard.showToast('Triggering load rebalancing...', 'info');
        
        const response = await fetch('/api/v1/load-balancer/rebalance', {
            method: 'POST'
        });
        const result = await response.json();
        
        if (response.ok && result.success) {
            dashboard.showToast('Load rebalancing completed!', 'success');
        } else {
            dashboard.showToast(`Load rebalancing failed: ${result.error || 'Unknown'}`, 'error');
        }
    } catch (error) {
        console.error('Error rebalancing load:', error);
        dashboard.showToast('Error rebalancing load', 'error');
    }
}

function refreshDashboard() {
    if (window.dashboard) {
        window.dashboard.refreshDashboard();
    }
}

async function testTaskModal() {
    try {
        // Find a completed task to test the modal
        const response = await fetch('/api/v1/tasks?limit=50');
        const data = await response.json();
        const completedTasks = data.tasks.filter(task => task.status === 'completed');
        
        if (completedTasks.length > 0) {
            const taskId = completedTasks[0].id;
            dashboard.showToast(`Opening modal for completed task ${taskId}`, 'info');
            await window.showTaskDetails(taskId);
        } else {
            dashboard.showToast('No completed tasks found to test modal', 'warning');
        }
    } catch (error) {
        console.error('Error testing task modal:', error);
        dashboard.showToast('Error testing task modal', 'error');
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
    // Expose showTaskDetails globally for onclick handlers
    window.showTaskDetails = (id) => window.dashboard.showTaskDetails(id);
    // Add refresh method to instance
    window.dashboard.refreshDashboard = () => window.dashboard.loadDashboardData();
});
