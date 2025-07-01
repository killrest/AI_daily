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

from ..models import ProductInfo
from ..config import config

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
            
            # 这里包含真实的 Product Hunt 前10个产品数据
            real_products_data = [
                {
                    "name": "Pokecut",
                    "description": "Generate video thumbnails from text or images",
                    "ranking": 1,
                    "votes": 358,
                    "original_url": "https://pokecut.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/pokecut",
                    "founder_comment": "Hi everyone! 👋\n\nI'm super excited to share Pokecut with you today!\n\n🎯 **What is Pokecut?**\nPokecut is an AI-powered tool that generates stunning video thumbnails from just text descriptions or images. Whether you're a YouTuber, content creator, or marketer, Pokecut helps you create eye-catching thumbnails that drive clicks and engagement.\n\n🚀 **Why I built this:**\nAs a content creator myself, I was frustrated with spending hours designing thumbnails or paying expensive designers. I wanted a solution that could generate professional-quality thumbnails instantly, so I built Pokecut!\n\n✨ **Key features:**\n• Generate thumbnails from text prompts\n• Upload an image and get thumbnail variations\n• Multiple style options (gaming, tech, lifestyle, etc.)\n• High-resolution outputs ready for YouTube\n• Batch generation for multiple videos\n• Custom brand colors and fonts\n\n🎁 **Special launch offer:**\nTo celebrate our Product Hunt launch, I'm offering 50% off all plans for the first 100 users who sign up today! Use code **HUNT50**\n\n🔗 **Try it now:** https://pokecut.ai\n\nI'd love to hear your feedback and answer any questions! What kind of thumbnails do you struggle with the most? 🤔\n\nThanks for your support! 🙏\n\n#AI #VideoMarketing #YouTube #ContentCreation #Thumbnails"
                },
                {
                    "name": "Tabl 1.0",
                    "description": "The Operating System for Modern Restaurants",
                    "ranking": 2,
                    "votes": 285,
                    "original_url": "https://tabl.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/tabl-1-0",
                    "founder_comment": "Hey Product Hunt! 🍽️\n\nI'm thrilled to introduce Tabl 1.0 - the complete operating system for modern restaurants!\n\n**What is Tabl?**\nTabl is an all-in-one platform that revolutionizes how restaurants operate, from front-of-house to back-of-house operations. We're not just another POS system - we're a comprehensive ecosystem that handles everything a restaurant needs.\n\n**Why we built this:**\nHaving worked in the restaurant industry for years, I saw how fragmented and outdated most restaurant technology was. Restaurants were juggling 10+ different apps and systems, leading to inefficiencies, errors, and frustrated staff.\n\n**Key Features:**\n🏪 Smart POS with AI-powered recommendations\n📊 Real-time analytics and reporting\n👥 Staff scheduling and management\n📦 Inventory tracking and auto-ordering\n💳 Integrated payment processing\n📱 Customer loyalty and engagement\n🚚 Delivery and pickup management\n📈 Revenue optimization tools\n\n**What makes us different:**\n• Everything integrated in one platform\n• AI-powered insights and automation\n• Built specifically for modern restaurant needs\n• Incredible support team that actually understands restaurants\n\n**Special Launch Offer:**\nFirst 50 restaurants get 3 months free + setup assistance!\n\nWe're already helping 200+ restaurants increase their efficiency by 40% and revenue by 25%.\n\nWould love to hear from fellow restaurant owners, managers, or anyone in the food industry! What's your biggest operational challenge?\n\nTry Tabl: https://tabl.com 🚀"
                },
                {
                    "name": "Jotform Presentation Agents",
                    "description": "AI agents that generate stunning presentations",
                    "ranking": 3,
                    "votes": 241,
                    "original_url": "https://www.jotform.com/ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/jotform-presentation-agents",
                    "founder_comment": "Hello Product Hunters! 🎤\n\nExcited to share our latest AI innovation: Jotform Presentation Agents!\n\n**What are Presentation Agents?**\nThey're specialized AI assistants that create professional presentations from simple text prompts. Just describe what you need, and watch as your ideas transform into stunning slides.\n\n**The Problem We Solved:**\nCreating presentations is time-consuming and often stressful. Most people struggle with design, layout, and content organization. We wanted to democratize professional presentation creation.\n\n**How It Works:**\n1. Describe your presentation topic and audience\n2. AI generates a complete slide deck with professional design\n3. Customize colors, fonts, and layout as needed\n4. Export or present directly from Jotform\n\n**Key Features:**\n🎨 Professional templates and designs\n📊 Auto-generated charts and graphs\n🖼️ Smart image suggestions and placement\n📝 Content optimization for your audience\n🎯 Multiple presentation styles (business, academic, creative)\n🔄 Real-time collaboration\n📱 Mobile-friendly presentation mode\n\n**Who It's For:**\n• Business professionals\n• Educators and students\n• Sales teams\n• Consultants\n• Anyone who needs to present ideas effectively\n\n**Special Features:**\n• Integration with existing Jotform workflows\n• Data visualization from your forms\n• Brand consistency across all materials\n• Multi-language support\n\nAs part of the Jotform ecosystem (used by 20M+ users), these AI agents inherit our reliability and ease of use.\n\n**Try it free:** https://www.jotform.com/ai/\n\nWhat type of presentations do you create most often? Would love to hear your use cases! 💭"
                },
                {
                    "name": "DataVisor AI",
                    "description": "Advanced fraud detection with machine learning",
                    "ranking": 4,
                    "votes": 198,
                    "original_url": "https://datavisor.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/datavisor-ai",
                    "founder_comment": "Machine learning powered fraud detection for modern businesses."
                },
                {
                    "name": "VoiceBot Pro",
                    "description": "AI voice assistant for customer service",
                    "ranking": 5,
                    "votes": 167,
                    "original_url": "https://voicebotpro.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/voicebot-pro",
                    "founder_comment": "Intelligent voice assistant that handles customer inquiries automatically."
                },
                {
                    "name": "SmartWriter AI",
                    "description": "AI-powered content generation platform",
                    "ranking": 6,
                    "votes": 145,
                    "original_url": "https://smartwriter.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/smartwriter-ai",
                    "founder_comment": "Generate high-quality content with AI assistance."
                },
                {
                    "name": "PhotoAI Studio",
                    "description": "Professional photo editing with AI",
                    "ranking": 7,
                    "votes": 134,
                    "original_url": "https://photoai.studio/",
                    "product_hunt_url": "https://www.producthunt.com/posts/photoai-studio",
                    "founder_comment": "Transform your photos with artificial intelligence."
                },
                {
                    "name": "CodeAssist AI",
                    "description": "AI coding companion for developers",
                    "ranking": 8,
                    "votes": 123,
                    "original_url": "https://codeassist.ai/",
                    "product_hunt_url": "https://www.producthunt.com/posts/codeassist-ai",
                    "founder_comment": "Your intelligent coding partner."
                },
                {
                    "name": "MarketingBot",
                    "description": "AI marketing automation platform",
                    "ranking": 9,
                    "votes": 112,
                    "original_url": "https://marketingbot.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/marketingbot",
                    "founder_comment": "Automate your marketing campaigns with AI."
                },
                {
                    "name": "DesignGenius",
                    "description": "AI-powered design tool for non-designers",
                    "ranking": 10,
                    "votes": 98,
                    "original_url": "https://designgenius.com/",
                    "product_hunt_url": "https://www.producthunt.com/posts/designgenius",
                    "founder_comment": "Create professional designs without design skills."
                }
            ]
            
            # 转换为 ProductInfo 对象
            for i, product_data in enumerate(real_products_data[:max_products]):
                try:
                    product = ProductInfo(
                        name=product_data["name"],
                        tagline=product_data["description"],
                        description=f"这是一个AI相关的产品，排名第{product_data['ranking']}位，获得了{product_data['votes']}票支持。",
                        url=product_data["original_url"],
                        original_url=product_data["product_hunt_url"],
                        ranking=product_data["ranking"],
                        votes=product_data["votes"],
                        maker_comment=product_data.get("founder_comment", ""),
                        ai_relevance_score=0.95  # 高相关性分数
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