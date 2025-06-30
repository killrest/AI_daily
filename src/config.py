"""
配置管理模块
负责加载和管理彩虹一号的各种配置
"""

import os
import yaml
from dotenv import load_dotenv
from typing import Dict, Any, List
from dataclasses import dataclass

# 加载环境变量
load_dotenv()

@dataclass
class AppConfig:
    """应用配置"""
    name: str
    version: str
    timezone: str

@dataclass
class SourceConfig:
    """信息源配置"""
    enabled: bool
    url: str
    api_url: str
    rate_limit: int

@dataclass
class AIConfig:
    """AI配置"""
    provider: str
    model: str
    temperature: float
    max_tokens: int
    api_key: str
    base_url: str = ""
    endpoint_id: str = ""

@dataclass
class FilteringConfig:
    """内容筛选配置"""
    ai_keywords: List[str]
    exclude_keywords: List[str]

@dataclass
class FeishuConfig:
    """飞书配置"""
    webhook_url: str
    webhook_secret: str
    app_id: str
    app_secret: str

@dataclass
class ScheduleConfig:
    """定时任务配置"""
    daily_report_time: str
    data_collection_time: str

@dataclass
class OutputConfig:
    """输出配置"""
    format: str
    include_images: bool
    max_products: int

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = config_file
        self._load_config()
        
    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            # 应用配置
            app_data = config_data.get('app', {})
            self.app = AppConfig(
                name=app_data.get('name', '彩虹一号'),
                version=app_data.get('version', '1.0.0'),
                timezone=app_data.get('timezone', 'Asia/Shanghai')
            )
            
            # 信息源配置
            ph_data = config_data.get('sources', {}).get('product_hunt', {})
            self.product_hunt = SourceConfig(
                enabled=ph_data.get('enabled', True),
                url=ph_data.get('url', 'https://www.producthunt.com'),
                api_url=ph_data.get('api_url', 'https://api.producthunt.com/v2/api/graphql'),
                rate_limit=ph_data.get('rate_limit', 60)
            )
            
            # AI配置
            ai_data = config_data.get('ai', {})
            provider = ai_data.get('provider', 'openai')
            
            # 根据provider选择合适的API密钥
            if provider == 'volcengine_ark':
                api_key = os.getenv('AI_API_KEY', os.getenv('VOLCENGINE_ARK_API_KEY', ''))
            else:
                api_key = os.getenv('AI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
                
            self.ai = AIConfig(
                provider=provider,
                model=ai_data.get('model', 'gpt-4'),
                temperature=ai_data.get('temperature', 0.3),
                max_tokens=ai_data.get('max_tokens', 2000),
                api_key=api_key,
                base_url=ai_data.get('base_url', ''),
                endpoint_id=ai_data.get('endpoint_id', '')
            )
            
            # 筛选配置
            filtering_data = config_data.get('filtering', {})
            self.filtering = FilteringConfig(
                ai_keywords=filtering_data.get('keywords', {}).get('ai_related', []),
                exclude_keywords=filtering_data.get('exclude_keywords', [])
            )
            
            # 飞书配置
            feishu_data = config_data.get('feishu', {})
            self.feishu = FeishuConfig(
                webhook_url=os.getenv('FEISHU_WEBHOOK_URL', feishu_data.get('webhook_url', '')),
                webhook_secret=os.getenv('FEISHU_WEBHOOK_SECRET', feishu_data.get('webhook_secret', '')),
                app_id=os.getenv('FEISHU_APP_ID', feishu_data.get('app_id', '')),
                app_secret=os.getenv('FEISHU_APP_SECRET', feishu_data.get('app_secret', ''))
            )
            
            # 定时任务配置
            schedule_data = config_data.get('schedule', {})
            self.schedule = ScheduleConfig(
                daily_report_time=schedule_data.get('daily_report_time', '09:00'),
                data_collection_time=schedule_data.get('data_collection_time', '08:00')
            )
            
            # 输出配置
            output_data = config_data.get('output', {})
            self.output = OutputConfig(
                format=output_data.get('format', 'markdown'),
                include_images=output_data.get('include_images', True),
                max_products=output_data.get('max_products', 10)
            )
            
        except Exception as e:
            print(f"配置加载失败: {e}")
            self._load_default_config()
    
    def _load_default_config(self):
        """加载默认配置"""
        self.app = AppConfig("彩虹一号", "1.0.0", "Asia/Shanghai")
        self.product_hunt = SourceConfig(True, "https://www.producthunt.com", 
                                       "https://api.producthunt.com/v2/api/graphql", 60)
        self.ai = AIConfig("volcengine_ark", "deepseek-v3", 0.3, 2000, 
                          os.getenv('AI_API_KEY', os.getenv('VOLCENGINE_ARK_API_KEY', '')),
                          "https://ark.cn-beijing.volces.com/api/v3",
                          "ep-m-20250413002708-ct9mc")
        self.filtering = FilteringConfig(
            ["AI", "artificial intelligence", "machine learning"], 
            ["unrelated", "spam"]
        )
        self.feishu = FeishuConfig(
            os.getenv('FEISHU_WEBHOOK_URL', ''),
            os.getenv('FEISHU_WEBHOOK_SECRET', ''),
            os.getenv('FEISHU_APP_ID', ''),
            os.getenv('FEISHU_APP_SECRET', '')
        )
        self.schedule = ScheduleConfig("09:00", "08:00")
        self.output = OutputConfig("markdown", True, 10)

# 全局配置实例
config = ConfigManager() 