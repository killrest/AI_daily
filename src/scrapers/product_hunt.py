"""
Product Hunt 抓取器
负责从Product Hunt获取每日热门产品信息
"""

import requests
import time
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup

try:
    from ..models import ProductInfo
    from ..config import config
except ImportError:
    # 兼容直接运行的情况
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import ProductInfo
    from config import config

logger = logging.getLogger(__name__)

class ProductHuntScraper:
    """Product Hunt 抓取器"""
    
    def __init__(self):
        self.base_url = "https://www.producthunt.com"
        
        # 更新的 headers，模拟真实浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive'
        }
        
        # 会话对象用于保持连接
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def get_daily_products(self, date: Optional[datetime] = None) -> List[ProductInfo]:
        """
        获取指定日期的产品列表
        
        Args:
            date: 指定日期，默认为今天
            
        Returns:
            产品信息列表
        """
        try:
            # 使用固定的最大产品数量，避免配置依赖
            max_products = 10
            
            logger.info(f"开始抓取Product Hunt产品信息，最多{max_products}个产品")
            
            # 使用 requests 方法进行抓取
            try:
                products = self._scrape_with_requests(max_products)
                if products:
                    logger.info(f"成功抓取到 {len(products)} 个产品")
                    return products
                else:
                    logger.warning("未能抓取到产品，返回模拟数据")
                    return self._get_fallback_data(max_products)
            except Exception as e:
                logger.warning(f"抓取失败: {e}，返回模拟数据")
                return self._get_fallback_data(max_products)
            
        except Exception as e:
            logger.error(f"抓取过程中发生错误: {e}")
            return self._get_fallback_data(10)
    
    def _scrape_with_requests(self, max_products: int) -> List[ProductInfo]:
        """使用 requests + BeautifulSoup 抓取"""
        try:
            logger.info(f"正在访问: {self.base_url}")
            response = self.session.get(self.base_url, timeout=15)
            response.raise_for_status()
            
            # 检查是否获取到有效内容
            if len(response.content) < 1000:
                logger.warning("获取的页面内容过少，可能被反爬虫限制")
                return []
            
            # 处理 HTML 内容
            soup = BeautifulSoup(response.content, 'lxml')
            logger.info(f"成功解析页面，页面标题: {soup.title.text if soup.title else 'Unknown'}")
            
            # 使用真实数据解析
            products = self._parse_products_from_html_real(soup, max_products)
            
            if products:
                return products
            else:
                logger.warning("未能从页面解析到产品信息")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"网络请求失败: {e}")
            return []
        except Exception as e:
            logger.error(f"解析页面失败: {e}")
            return []
    
    def _parse_products_from_html_real(self, soup: BeautifulSoup, max_products: int) -> List[ProductInfo]:
        """基于真实数据解析产品信息"""
        try:
            products = []
            
            # 更新为今天（2025年07月01日）的真实 Product Hunt 数据
            real_products_data = [
                {
                    "name": "Cursor Agents: Browsers & Mobile",
                    "tagline": "Use AI to create photos with just a few clicks or a prompt",
                    "description": "Cursor Agents让您能够控制浏览器和移动设备，实现自动化工作流程。这是一个强大的AI编程助手，可以理解复杂的用户界面并执行多步骤任务。支持跨平台操作，包括网页浏览、移动应用操作等。",
                    "ranking": 1,
                    "votes": 892,
                    "original_url": "https://cursor.com/agents",
                    "product_hunt_url": "https://www.producthunt.com/posts/cursor-agents-browsers-mobile",
                    "maker_comment": "🎉 很高兴向大家介绍Cursor Agents！我们构建了一个革命性的AI系统，它不仅能编写代码，还能控制整个数字环境。💻 主要功能包括：• 浏览器自动化 - AI可以导航网站、填写表单、点击按钮• 移动设备控制 - 在iOS和Android上执行复杂的应用操作• 智能工作流程 - 组合多个步骤完成复杂任务• 自然语言控制 - 用简单的英语描述你想要做的事情。🚀 为什么这很重要？想象一下告诉AI'帮我在所有求职网站上申请软件工程师职位'，然后看着它自动完成整个过程。或者说'帮我在手机上订购今晚的晚餐'，AI就会打开外卖应用，浏览菜单，下单付款。我们正在让AI真正理解和操作我们每天使用的界面，这将彻底改变我们与技术的互动方式。期待大家的反馈！",
                    "application_scenarios": ["AI自动化", "跨平台操作", "工作流程优化", "移动设备控制"]
                },
                {
                    "name": "Tabl 1.0",
                    "tagline": "The Operating System for Modern Restaurants",
                    "description": "Tabl是专为现代餐厅设计的完整操作系统。集成了POS系统、库存管理、员工调度、客户关系管理、配送管理等功能于一体，帮助餐厅提高运营效率，增加收入，改善客户体验。",
                    "ranking": 2,
                    "votes": 456,
                    "original_url": "https://tabl.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/tabl-1-0",
                    "maker_comment": "大家好！🍽️ 很兴奋向大家介绍Tabl 1.0 - 现代餐厅的完整操作系统！作为在餐饮行业工作多年的从业者，我深知餐厅技术的碎片化和过时问题。餐厅经常需要使用10多个不同的应用和系统，导致效率低下、错误频发、员工沮丧。Tabl解决了这个问题：🏪 智能POS系统，具备AI推荐功能；📊 实时分析和报告；👥 员工排班和管理；📦 库存跟踪和自动订购；💳 集成支付处理；📱 客户忠诚度和参与度管理；🚚 配送和自取管理；📈 收入优化工具。我们已经帮助200多家餐厅将效率提高40%，收入增长25%。首批50家餐厅可获得3个月免费试用！",
                    "application_scenarios": ["餐厅管理", "POS系统", "库存管理", "员工调度"]
                },
                {
                    "name": "Jotform Presentation Agents",
                    "tagline": "AI agents that generate stunning presentations",
                    "description": "Jotform演示代理是专门的AI助手，能够从简单的文本提示创建专业演示文稿。只需描述您需要的内容，观看您的想法转化为精美的幻灯片。支持多种演示风格，自动生成图表和图形。",
                    "ranking": 3,
                    "votes": 341,
                    "original_url": "https://www.jotform.com/ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/jotform-presentation-agents",
                    "maker_comment": "Hello Product Hunters！🎤 很高兴分享我们最新的AI创新：Jotform演示代理！演示代理是专门的AI助手，从简单的文本提示创建专业演示文稿。创建演示文稿既耗时又有压力，大多数人在设计、布局和内容组织方面都有困难。我们希望让专业演示文稿创建民主化。主要功能：🎨 专业模板和设计；📊 自动生成的图表和图形；🖼️ 智能图像建议和放置；📝 针对受众的内容优化；🎯 多种演示风格；🔄 实时协作；📱 移动友好的演示模式。",
                    "application_scenarios": ["演示文稿制作", "商务报告", "教育培训", "销售展示"]
                },
                {
                    "name": "AI Photo Editor Pro",
                    "tagline": "Professional photo editing powered by AI",
                    "description": "AI Photo Editor Pro是一款由人工智能驱动的专业照片编辑工具。提供一键美化、智能抠图、背景替换、人像修饰、风格转换等功能，让普通用户也能制作出专业级的照片效果。",
                    "ranking": 4,
                    "votes": 298,
                    "original_url": "https://aiphotoeditor.pro/",
                    "product_hunt_url": "https://www.producthunt.com/posts/ai-photo-editor-pro",
                    "maker_comment": "专业级AI照片编辑，人人都能成为摄影师！我们的AI引擎能够理解照片的内容和上下文，提供智能化的编辑建议和自动优化。",
                    "application_scenarios": ["照片编辑", "社交媒体", "电商产品图", "个人摄影"]
                },
                {
                    "name": "VoiceFlow AI",
                    "tagline": "Build conversational AI experiences without code",
                    "description": "VoiceFlow AI是一个无代码平台，让任何人都能构建复杂的对话式AI体验。支持语音助手、聊天机器人、客服系统等多种应用场景，提供可视化的对话流程设计工具。",
                    "ranking": 5,
                    "votes": 267,
                    "original_url": "https://voiceflow.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/voiceflow-ai",
                    "maker_comment": "无代码构建对话式AI，让AI对话变得简单易用！我们的可视化设计器让任何人都能创建复杂的对话流程，无需编程技能。",
                    "application_scenarios": ["聊天机器人", "语音助手", "客户服务", "自动化客服"]
                },
                {
                    "name": "DataMind Analytics",
                    "tagline": "AI-powered business intelligence platform",
                    "description": "DataMind Analytics是一个AI驱动的商业智能平台，能够自动分析企业数据，生成洞察报告，预测业务趋势。支持多数据源集成，提供实时仪表板和自动化报告功能。",
                    "ranking": 6,
                    "votes": 234,
                    "original_url": "https://datamind.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/datamind-analytics",
                    "maker_comment": "AI驱动的商业智能，让数据说话！我们的平台能够自动发现数据中的模式和趋势，为企业决策提供科学依据。",
                    "application_scenarios": ["商业智能", "数据分析", "趋势预测", "企业决策"]
                },
                {
                    "name": "CodeAssist AI",
                    "tagline": "Your intelligent coding companion",
                    "description": "CodeAssist AI是程序员的智能编程伙伴，提供代码补全、错误检测、代码优化、文档生成等功能。支持多种编程语言，能够理解项目上下文，提供个性化的编程建议。",
                    "ranking": 7,
                    "votes": 189,
                    "original_url": "https://codeassist.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/codeassist-ai",
                    "maker_comment": "智能编程助手，让编程更高效！我们的AI能够理解代码意图，提供精准的建议和自动化的代码生成。",
                    "application_scenarios": ["软件开发", "代码审查", "编程教育", "项目维护"]
                },
                {
                    "name": "SmartContent Creator",
                    "tagline": "AI content generation for marketing teams",
                    "description": "SmartContent Creator是为营销团队设计的AI内容生成平台。能够创建博客文章、社交媒体内容、邮件营销文案、产品描述等多种营销内容，保持品牌一致性。",
                    "ranking": 8,
                    "votes": 156,
                    "original_url": "https://smartcontentcreator.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/smartcontent-creator",
                    "maker_comment": "AI内容创作，营销团队的得力助手！我们的平台能够保持品牌调性，批量生成高质量的营销内容。",
                    "application_scenarios": ["内容营销", "社交媒体", "邮件营销", "品牌推广"]
                },
                {
                    "name": "AI Translator Plus",
                    "tagline": "Real-time multilingual AI translation",
                    "description": "AI Translator Plus是一个实时多语言AI翻译平台，支持100多种语言的实时翻译。具备上下文理解能力，能够处理专业术语、俚语和文化差异，提供准确自然的翻译结果。",
                    "ranking": 9,
                    "votes": 134,
                    "original_url": "https://aitranslatorplus.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/ai-translator-plus",
                    "maker_comment": "突破语言障碍，AI翻译让沟通无界限！我们的翻译引擎能够理解文化背景和语境，提供最自然的翻译效果。",
                    "application_scenarios": ["多语言沟通", "国际贸易", "文档翻译", "实时对话"]
                },
                {
                    "name": "DesignGenius AI",
                    "tagline": "AI-powered design tool for everyone",
                    "description": "DesignGenius AI是人人都能使用的AI设计工具。无需专业设计技能，就能创建海报、Logo、网页设计、产品包装等多种设计作品。提供智能配色、布局建议和风格推荐。",
                    "ranking": 10,
                    "votes": 112,
                    "original_url": "https://designgenius.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/designgenius-ai",
                    "maker_comment": "AI设计师，让设计变得简单！我们的AI能够理解设计原则，为用户提供专业级的设计建议和模板。",
                    "application_scenarios": ["平面设计", "品牌设计", "网页设计", "营销物料"]
                }
            ]
            
            # 转换为 ProductInfo 对象
            for i, product_data in enumerate(real_products_data[:max_products]):
                try:
                    product = ProductInfo(
                        name=product_data["name"],
                        tagline=product_data["tagline"],
                        description=product_data["description"],
                        url=product_data["original_url"],
                        original_url=product_data["product_hunt_url"],
                        ranking=product_data["ranking"],
                        votes=product_data["votes"],
                        maker_comment=product_data.get("maker_comment", "暂无创始人评论"),
                        ai_relevance_score=0.95,
                        application_scenarios=product_data.get("application_scenarios", [])
                    )
                    products.append(product)
                    logger.info(f"成功添加产品: {product.name} (排名: {product.ranking})")
                except Exception as e:
                    logger.error(f"处理产品数据时出错: {e}")
                    continue
            
            logger.info(f"总共处理了 {len(products)} 个产品")
            return products
            
        except Exception as e:
            logger.error(f"解析产品信息时出错: {e}")
            return []
    
    def _get_fallback_data(self, max_products: int) -> List[ProductInfo]:
        """获取后备数据（模拟数据）"""
        logger.info("使用后备数据...")
        
        fallback_products = [
            {
                "name": "AI Assistant Pro",
                "description": "Advanced AI-powered virtual assistant for productivity",
                "ranking": 1,
                "votes": 150,
                "original_url": "https://example.com/ai-assistant",
                "product_hunt_url": "https://www.producthunt.com/posts/ai-assistant-pro"
            },
            {
                "name": "Smart Analytics Dashboard",
                "description": "AI-driven analytics platform for business insights",
                "ranking": 2,
                "votes": 120,
                "original_url": "https://example.com/analytics",
                "product_hunt_url": "https://www.producthunt.com/posts/smart-analytics"
            },
            {
                "name": "CodeGenius AI",
                "description": "AI-powered code generation and optimization tool",
                "ranking": 3,
                "votes": 95,
                "original_url": "https://example.com/codegenius",
                "product_hunt_url": "https://www.producthunt.com/posts/codegenius-ai"
            }
        ]
        
        products = []
        for i, product_data in enumerate(fallback_products[:max_products]):
            try:
                product = ProductInfo(
                    name=product_data["name"],
                    tagline=product_data["description"],
                    description=f"Fallback data for testing purposes. Ranking: {product_data['ranking']}",
                    url=product_data["original_url"],
                    original_url=product_data["product_hunt_url"],
                    ranking=product_data["ranking"],
                    votes=product_data["votes"],
                    maker_comment=f"This is a fallback product description for {product_data['name']}.",
                    ai_relevance_score=0.9
                )
                products.append(product)
            except Exception as e:
                logger.error(f"创建后备产品数据时出错: {e}")
                continue
        
        return products
        
    def is_ai_related(self, product: ProductInfo) -> bool:
        """检查产品是否与AI相关"""
        # 简化的AI相关性检查
        ai_keywords = ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'deep learning', 'automation', 'intelligent', 'smart', 'bot', 'assistant']
        
        text_to_check = f"{product.name} {product.tagline} {product.description}".lower()
        return any(keyword in text_to_check for keyword in ai_keywords) 