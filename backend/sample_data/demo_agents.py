"""
Sample Agents for Demonstration and Testing
"""
import asyncio
from typing import Dict, Any, List
from backend.agents.base_agent import SpecializedAgent
from backend.database.models import AgentStatus


class DataAnalystAgent(SpecializedAgent):
    """Agent specialized in data analysis and visualization"""
    
    def __init__(self):
        super().__init__(
            name="DataAnalyst-Alpha",
            description="Expert in data analysis, statistics, and visualization",
            capabilities=[
                "data_analysis", "statistical_modeling", "data_visualization", 
                "pattern_recognition", "predictive_analytics", "data_cleaning"
            ],
            domain="data_science",
            specialized_tools=["pandas", "numpy", "matplotlib", "seaborn", "scikit-learn"],
            resource_requirements={
                "cpu": 0.3,
                "memory": 0.4,
                "storage": 0.2
            }
        )
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data analysis tasks"""
        task_type = task_data.get('type', 'general_analysis')
        
        if task_type == 'statistical_analysis':
            return await self._perform_statistical_analysis(task_data)
        elif task_type == 'data_visualization':
            return await self._create_visualization(task_data)
        elif task_type == 'predictive_modeling':
            return await self._build_predictive_model(task_data)
        else:
            return await super().execute_task(task_data)
    
    async def _perform_statistical_analysis(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on provided data"""
        # Simulate analysis work
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'analysis_type': 'statistical_analysis',
            'results': {
                'mean': 42.5,
                'std_dev': 12.3,
                'correlation_matrix': [[1.0, 0.7], [0.7, 1.0]],
                'p_values': [0.001, 0.05],
                'confidence_interval': [38.2, 46.8]
            },
            'insights': [
                'Strong positive correlation detected between variables',
                'Data shows normal distribution with slight right skew',
                'Statistical significance achieved at p < 0.05'
            ]
        }
    
    async def _create_visualization(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create data visualizations"""
        await asyncio.sleep(1.5)
        
        return {
            'success': True,
            'visualization_type': 'multi_chart_dashboard',
            'charts_created': [
                'scatter_plot', 'histogram', 'box_plot', 'correlation_heatmap'
            ],
            'file_paths': [
                '/tmp/scatter_analysis.png',
                '/tmp/distribution_hist.png',
                '/tmp/outlier_boxplot.png',
                '/tmp/correlation_heatmap.png'
            ]
        }
    
    async def _build_predictive_model(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build predictive models"""
        await asyncio.sleep(3)
        
        return {
            'success': True,
            'model_type': 'random_forest_classifier',
            'performance_metrics': {
                'accuracy': 0.87,
                'precision': 0.85,
                'recall': 0.89,
                'f1_score': 0.87
            },
            'feature_importance': {
                'feature_1': 0.35,
                'feature_2': 0.28,
                'feature_3': 0.22,
                'feature_4': 0.15
            }
        }


class NLPAgent(SpecializedAgent):
    """Agent specialized in natural language processing"""
    
    def __init__(self):
        super().__init__(
            name="NLP-Processor-Beta",
            description="Expert in natural language processing and text analysis",
            capabilities=[
                "text_analysis", "sentiment_analysis", "entity_extraction",
                "language_translation", "text_summarization", "topic_modeling"
            ],
            domain="natural_language_processing",
            specialized_tools=["spacy", "nltk", "transformers", "gensim"],
            resource_requirements={
                "cpu": 0.4,
                "memory": 0.6,
                "gpu": 0.3
            }
        )
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute NLP tasks"""
        task_type = task_data.get('type', 'text_analysis')
        
        if task_type == 'sentiment_analysis':
            return await self._analyze_sentiment(task_data)
        elif task_type == 'entity_extraction':
            return await self._extract_entities(task_data)
        elif task_type == 'text_summarization':
            return await self._summarize_text(task_data)
        else:
            return await super().execute_task(task_data)
    
    async def _analyze_sentiment(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'sentiment_scores': {
                'positive': 0.7,
                'negative': 0.2,
                'neutral': 0.1
            },
            'overall_sentiment': 'positive',
            'confidence': 0.85,
            'key_phrases': ['excellent service', 'highly recommend', 'great experience']
        }
    
    async def _extract_entities(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract named entities from text"""
        await asyncio.sleep(1.5)
        
        return {
            'success': True,
            'entities': {
                'PERSON': ['John Smith', 'Mary Johnson'],
                'ORG': ['OpenAI', 'Microsoft'],
                'GPE': ['New York', 'California'],
                'DATE': ['2024-01-15', 'next week'],
                'MONEY': ['$1000', '$50K']
            },
            'entity_count': 7
        }
    
    async def _summarize_text(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize long text"""
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'summary': 'The document discusses the implementation of a multi-agent system for complex task orchestration, highlighting key features like agent coordination, conflict resolution, and performance monitoring.',
            'key_points': [
                'Multi-agent coordination is essential for complex tasks',
                'Conflict resolution mechanisms ensure system stability',
                'Performance monitoring enables optimization'
            ],
            'compression_ratio': 0.15
        }


class WebScraperAgent(SpecializedAgent):
    """Agent specialized in web scraping and data collection"""
    
    def __init__(self):
        super().__init__(
            name="WebScraper-Gamma",
            description="Expert in web scraping, data extraction, and web automation",
            capabilities=[
                "web_scraping", "data_extraction", "web_automation",
                "api_integration", "content_parsing", "data_validation"
            ],
            domain="web_automation",
            specialized_tools=["selenium", "beautifulsoup", "scrapy", "requests"],
            resource_requirements={
                "cpu": 0.2,
                "memory": 0.3,
                "network": 0.8
            }
        )
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute web scraping tasks"""
        task_type = task_data.get('type', 'web_scraping')
        
        if task_type == 'scrape_website':
            return await self._scrape_website(task_data)
        elif task_type == 'api_data_collection':
            return await self._collect_api_data(task_data)
        elif task_type == 'content_monitoring':
            return await self._monitor_content(task_data)
        else:
            return await super().execute_task(task_data)
    
    async def _scrape_website(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape data from websites"""
        await asyncio.sleep(2.5)
        
        return {
            'success': True,
            'pages_scraped': 25,
            'data_points_collected': 150,
            'data_types': ['product_info', 'prices', 'reviews', 'ratings'],
            'file_output': '/tmp/scraped_data.json',
            'scraping_duration': '2.5 seconds'
        }
    
    async def _collect_api_data(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect data from APIs"""
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'api_calls_made': 10,
            'records_retrieved': 500,
            'rate_limit_status': 'within_limits',
            'data_freshness': 'real_time',
            'cache_hit_ratio': 0.3
        }
    
    async def _monitor_content(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor content changes"""
        await asyncio.sleep(1.5)
        
        return {
            'success': True,
            'changes_detected': 3,
            'change_types': ['price_update', 'new_content', 'structure_change'],
            'monitoring_period': '24_hours',
            'alert_threshold_reached': False
        }


class ReportGeneratorAgent(SpecializedAgent):
    """Agent specialized in report generation and documentation"""
    
    def __init__(self):
        super().__init__(
            name="ReportGen-Delta",
            description="Expert in generating reports, documentation, and presentations",
            capabilities=[
                "report_generation", "document_creation", "data_presentation",
                "template_processing", "chart_creation", "pdf_generation"
            ],
            domain="document_processing",
            specialized_tools=["reportlab", "jinja2", "matplotlib", "docx"],
            resource_requirements={
                "cpu": 0.2,
                "memory": 0.3,
                "storage": 0.4
            }
        )
    
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute report generation tasks"""
        task_type = task_data.get('type', 'generate_report')
        
        if task_type == 'analytical_report':
            return await self._generate_analytical_report(task_data)
        elif task_type == 'executive_summary':
            return await self._create_executive_summary(task_data)
        elif task_type == 'technical_documentation':
            return await self._create_technical_docs(task_data)
        else:
            return await super().execute_task(task_data)
    
    async def _generate_analytical_report(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analytical report"""
        await asyncio.sleep(3)
        
        return {
            'success': True,
            'report_type': 'analytical_report',
            'sections_created': [
                'executive_summary', 'methodology', 'findings', 
                'recommendations', 'appendices'
            ],
            'page_count': 25,
            'charts_included': 8,
            'output_formats': ['pdf', 'docx', 'html'],
            'file_paths': [
                '/tmp/analytical_report.pdf',
                '/tmp/analytical_report.docx'
            ]
        }
    
    async def _create_executive_summary(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create executive summary"""
        await asyncio.sleep(1)
        
        return {
            'success': True,
            'summary_length': '2_pages',
            'key_metrics_highlighted': 5,
            'recommendations_count': 3,
            'stakeholder_focus': 'c_suite',
            'delivery_format': 'presentation_ready'
        }
    
    async def _create_technical_docs(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create technical documentation"""
        await asyncio.sleep(2)
        
        return {
            'success': True,
            'documentation_type': 'api_documentation',
            'endpoints_documented': 15,
            'code_examples_included': 25,
            'interactive_features': ['code_playground', 'request_builder'],
            'output_format': 'interactive_html'
        }


# Sample agent factory
class SampleAgentFactory:
    """Factory for creating sample agents"""
    
    @staticmethod
    def create_sample_agents() -> List[SpecializedAgent]:
        """Create a set of sample agents for demonstration"""
        return [
            DataAnalystAgent(),
            NLPAgent(),
            WebScraperAgent(),
            ReportGeneratorAgent()
        ]
    
    @staticmethod
    def get_agent_by_capability(capability: str) -> List[SpecializedAgent]:
        """Get agents that have a specific capability"""
        agents = SampleAgentFactory.create_sample_agents()
        
        matching_agents = []
        for agent in agents:
            if capability.lower() in [cap.lower() for cap in agent.capabilities]:
                matching_agents.append(agent)
        
        return matching_agents
