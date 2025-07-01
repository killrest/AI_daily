"""
日报生成器
根据分析结果生成结构化的AI产品日报
"""

import logging
from typing import List
from datetime import datetime, timezone
import pytz

from .models import ProductInfo, DailyReport
from .config import config

logger = logging.getLogger(__name__)

class ReportGenerator:
    """日报生成器"""
    
    def __init__(self):
        self.timezone = pytz.timezone(config.app.timezone)
        
    def generate_daily_report(self, products: List[ProductInfo], analysis_summary: str) -> DailyReport:
        """生成每日日报"""
        current_time = datetime.now(self.timezone)
        
        report = DailyReport(
            date=current_time,
            products=products,
            summary=analysis_summary,
            total_products_analyzed=len(products),
            ai_relevant_products=len(products)
        )
        
        return report
    
    def format_report_as_markdown(self, report: DailyReport) -> str:
        """将日报格式化为Markdown格式"""
        date_str = report.date.strftime("%Y年%m月%d日")
        
        markdown_content = f"""🌈 彩虹一号 AI 日报 - {date_str}

"""
        
        # 添加每个产品的详细信息
        for i, product in enumerate(report.products, 1):
            product_section = self._format_single_product(product, i)
            markdown_content += product_section + "\n\n"
        
        return markdown_content
    
    def _format_single_product(self, product: ProductInfo, index: int) -> str:
        """格式化单个产品信息，严格按照用户要求的格式"""
        
        # 应用场景列表
        scenarios_text = ""
        if product.application_scenarios and len(product.application_scenarios) > 0:
            scenarios_text = "、".join(product.application_scenarios)
        else:
            scenarios_text = "AI应用场景"
        
        # 详细功能介绍 - 综合产品描述和tagline
        detailed_intro = ""
        if product.description:
            detailed_intro = product.description
        elif product.tagline:
            detailed_intro = product.tagline
        else:
            detailed_intro = "暂无详细介绍"
        
        # 创始人评论 - 使用完整的maker_comment
        founder_comment = ""
        if product.maker_comment and product.maker_comment != "暂无创始人评论":
            founder_comment = product.maker_comment
        else:
            founder_comment = "暂无创始人评论"
        
        # 构建产品报告（严格按照用户要求的格式）
        product_report = f"""# {product.name} - {product.tagline}
- 排名：第 {product.ranking} 名
- 项目名称：{product.name}
- 详细功能介绍：{detailed_intro}
- 应用场景：{scenarios_text}
- 创始人评论：{founder_comment}
- 原始链接：{product.url or '暂无官网链接'}
- Product hunt链接：{product.original_url}"""
        
        return product_report
    
    def format_report_as_feishu_card(self, report: DailyReport) -> dict:
        """将日报格式化为飞书富文本卡片格式"""
        date_str = report.date.strftime("%Y年%m月%d日")
        
        # 构建飞书卡片内容
        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"🌈 **彩虹一号 AI 产品日报** - {date_str}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"📊 **今日概览**\n- 分析产品总数: {report.total_products_analyzed}\n- AI相关产品: {report.ai_relevant_products}\n- 报告生成时间: {report.date.strftime('%Y-%m-%d %H:%M:%S')}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "div",
                    "text": {
                        "content": f"🤖 **AI趋势分析**\n{report.summary}",
                        "tag": "lark_md"
                    }
                },
                {
                    "tag": "hr"
                }
            ]
        }
        
        # 添加产品详情（取前5个产品，避免内容过长）
        for i, product in enumerate(report.products[:5], 1):
            product_element = {
                "tag": "div",
                "text": {
                    "content": self._format_product_for_feishu(product, i),
                    "tag": "lark_md"
                }
            }
            card_content["elements"].append(product_element)
            
            # 添加分割线（除最后一个）
            if i < min(len(report.products), 5):
                card_content["elements"].append({"tag": "hr"})
        
        # 如果产品超过5个，添加省略提示
        if len(report.products) > 5:
            card_content["elements"].append({
                "tag": "div",
                "text": {
                    "content": f"... 还有 {len(report.products) - 5} 个AI产品，详情请查看完整报告",
                    "tag": "lark_md"
                }
            })
        
        # 添加底部信息
        card_content["elements"].extend([
            {"tag": "hr"},
            {
                "tag": "div",
                "text": {
                    "content": f"*报告由彩虹一号AI日报系统自动生成 | {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S')}*",
                    "tag": "lark_md"
                }
            }
        ])
        
        return card_content
    
    def _format_product_for_feishu(self, product: ProductInfo, index: int) -> str:
        """为飞书格式化单个产品信息（简化版）"""
        scenarios = "、".join(product.application_scenarios) if product.application_scenarios else "通用AI应用"
        
        content = f"""**{index}. {product.name}** - {product.tagline}
🏆 排名: 第 {product.ranking} 名 | 🗳️ 票数: {product.votes}
🎯 **应用场景**: {scenarios}
💡 **相关性评分**: {product.ai_relevance_score:.1f}/1.0
🔗 [查看详情]({product.original_url})"""

        if product.translated_description and len(product.translated_description) < 150:
            content += f"\n📝 **产品介绍**: {product.translated_description}"
        
        # 添加创始人洞察（如果内容不太长）
        if product.founder_insights and len(product.founder_insights) < 200 and product.founder_insights != '暂无创始人评论信息':
            content += f"\n👨‍💼 **创始人想法**: {product.founder_insights}"
            
        return content
    
    def save_report(self, report: DailyReport, format_type: str = "markdown") -> str:
        """保存报告到文件"""
        date_str = report.date.strftime("%Y%m%d")
        
        if format_type == "markdown":
            content = self.format_report_as_markdown(report)
        elif format_type == "json":
            content = report.to_json()
        else:
            raise ValueError(f"不支持的格式类型: {format_type}")
        
        try:
            import os
            
            # 检查是否在 serverless 环境中
            is_serverless = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
            
            if is_serverless:
                # 在 serverless 环境中，使用 /tmp 目录
                base_dir = "/tmp"
                filename = f"{base_dir}/ai_daily_report_{date_str}.{format_type}"
            else:
                # 在本地环境中，使用 reports 目录
                base_dir = "reports"
                os.makedirs(base_dir, exist_ok=True)
                filename = f"{base_dir}/ai_daily_report_{date_str}.{format_type}"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
                
            logger.info(f"报告已保存到: {filename}")
            return filename
            
        except Exception as e:
            import os
            # 检查是否在 serverless 环境中
            is_serverless = os.environ.get('VERCEL') or os.environ.get('AWS_LAMBDA_FUNCTION_NAME')
            
            # 在 serverless 环境中，如果保存失败，只记录警告而不抛出异常
            if is_serverless:
                logger.warning(f"保存报告失败(serverless环境): {e}")
                return f"temp_report_{date_str}.{format_type}"
            else:
                logger.error(f"保存报告失败: {e}")
                raise 