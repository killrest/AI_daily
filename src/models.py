"""
数据模型定义
定义产品信息和日报的数据结构
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

@dataclass
class ProductInfo:
    """产品信息数据模型"""
    name: str
    tagline: str  # 一句话介绍
    description: str  # 详细描述
    url: str  # 产品链接
    original_url: str  # 原始链接（Product Hunt链接）
    ranking: int  # 排名
    votes: int  # 投票数
    maker_comment: Optional[str] = None  # 创始人介绍
    founder_insights: Optional[str] = None  # AI分析的创始人洞察
    category: Optional[str] = None  # 分类
    tags: List[str] = None  # 标签
    screenshot_url: Optional[str] = None  # 截图链接
    logo_url: Optional[str] = None  # Logo链接
    created_at: Optional[datetime] = None  # 创建时间
    
    # AI分析结果
    ai_relevance_score: float = 0.0  # AI相关性评分
    application_scenarios: List[str] = None  # 应用场景
    translated_description: str = ""  # 翻译后的描述
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.application_scenarios is None:
            self.application_scenarios = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'name': self.name,
            'tagline': self.tagline,
            'description': self.description,
            'url': self.url,
            'original_url': self.original_url,
            'ranking': self.ranking,
            'votes': self.votes,
            'maker_comment': self.maker_comment,
            'founder_insights': self.founder_insights,
            'category': self.category,
            'tags': self.tags,
            'screenshot_url': self.screenshot_url,
            'logo_url': self.logo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ai_relevance_score': self.ai_relevance_score,
            'application_scenarios': self.application_scenarios,
            'translated_description': self.translated_description
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductInfo':
        """从字典创建实例"""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
            
        return cls(
            name=data['name'],
            tagline=data['tagline'],
            description=data['description'],
            url=data['url'],
            original_url=data['original_url'],
            ranking=data['ranking'],
            votes=data['votes'],
            maker_comment=data.get('maker_comment'),
            founder_insights=data.get('founder_insights'),
            category=data.get('category'),
            tags=data.get('tags', []),
            screenshot_url=data.get('screenshot_url'),
            logo_url=data.get('logo_url'),
            created_at=created_at,
            ai_relevance_score=data.get('ai_relevance_score', 0.0),
            application_scenarios=data.get('application_scenarios', []),
            translated_description=data.get('translated_description', '')
        )

@dataclass
class DailyReport:
    """日报数据模型"""
    date: datetime
    products: List[ProductInfo]
    summary: str  # 总结
    ai_trend_analysis: str = ""  # AI趋势分析
    total_products_analyzed: int = 0  # 分析的产品总数
    ai_relevant_products: int = 0  # AI相关产品数量
    
    def __post_init__(self):
        self.ai_relevant_products = len(self.products)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'date': self.date.isoformat(),
            'products': [product.to_dict() for product in self.products],
            'summary': self.summary,
            'ai_trend_analysis': self.ai_trend_analysis,
            'total_products_analyzed': self.total_products_analyzed,
            'ai_relevant_products': self.ai_relevant_products
        }
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyReport':
        """从字典创建实例"""
        return cls(
            date=datetime.fromisoformat(data['date']),
            products=[ProductInfo.from_dict(p) for p in data['products']],
            summary=data['summary'],
            ai_trend_analysis=data.get('ai_trend_analysis', ''),
            total_products_analyzed=data.get('total_products_analyzed', 0),
            ai_relevant_products=data.get('ai_relevant_products', 0)
        ) 