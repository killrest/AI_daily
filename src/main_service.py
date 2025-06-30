"""
彩虹一号主服务
整合数据抓取、AI分析、报告生成和飞书推送等功能
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
import pytz

from .config import config
from .models import ProductInfo, DailyReport
from .scrapers.product_hunt import ProductHuntScraper
from .ai_analyzer import AIAnalyzer
from .report_generator import ReportGenerator
from .feishu_sender import FeishuSender

logger = logging.getLogger(__name__)

class RainbowOneService:
    """彩虹一号主服务"""
    
    def __init__(self):
        self.scraper = ProductHuntScraper()
        self.ai_analyzer = AIAnalyzer()
        self.report_generator = ReportGenerator()
        
        # 初始化飞书发送器，支持加签验证
        webhook_url = config.feishu.webhook_url
        webhook_secret = config.feishu.webhook_secret
        self.feishu_sender = FeishuSender(webhook_url, webhook_secret)
        
        self.timezone = pytz.timezone(config.app.timezone)
        
        # 缓存最新的产品数据和报告
        self.latest_products: List[ProductInfo] = []
        self.latest_report: Optional[DailyReport] = None
        
    def collect_and_analyze_data(self) -> bool:
        """收集并分析数据"""
        try:
            logger.info("开始收集Product Hunt数据")
            
            # 1. 抓取Product Hunt数据
            raw_products = self.scraper.get_daily_products()
            
            if not raw_products:
                logger.warning("未获取到任何产品数据")
                return False
            
            logger.info(f"获取到 {len(raw_products)} 个产品")
            
            # 2. 去重处理
            unique_products = self.ai_analyzer.remove_duplicates(raw_products)
            logger.info(f"去重后剩余 {len(unique_products)} 个产品")
            
            # 3. AI分析和筛选
            logger.info("开始AI分析和筛选")
            ai_products = self.ai_analyzer.analyze_products(unique_products)
            
            if not ai_products:
                logger.info("今日无AI相关产品")
                ai_products = []
            else:
                logger.info(f"筛选出 {len(ai_products)} 个AI相关产品")
            
            # 4. 缓存结果
            self.latest_products = ai_products
            
            return True
            
        except Exception as e:
            logger.error(f"数据收集和分析失败: {e}")
            return False
    
    def generate_and_send_report(self) -> bool:
        """生成并发送日报"""
        try:
            # 如果没有缓存数据，先尝试收集
            if not self.latest_products:
                logger.info("没有缓存数据，开始收集数据")
                if not self.collect_and_analyze_data():
                    logger.error("数据收集失败，无法生成报告")
                    return False
            
            # 生成AI趋势分析总结
            logger.info("生成AI趋势分析")
            analysis_summary = self.ai_analyzer.generate_daily_summary(self.latest_products)
            
            # 生成日报
            logger.info("生成每日报告")
            report = self.report_generator.generate_daily_report(
                self.latest_products, 
                analysis_summary
            )
            
            # 保存报告到文件
            try:
                markdown_file = self.report_generator.save_report(report, "markdown")
                json_file = self.report_generator.save_report(report, "json")
                logger.info(f"报告已保存: {markdown_file}, {json_file}")
            except Exception as e:
                logger.warning(f"保存报告文件失败: {e}")
            
            # 发送到飞书（使用文本消息格式）
            logger.info("发送报告到飞书")
            try:
                success = self.feishu_sender.send_daily_report(report)
            except Exception as e:
                logger.error(f"飞书消息发送异常: {e}")
                success = False
            
            if success:
                logger.info("报告发送成功")
                self.latest_report = report
                return True
            else:
                logger.error("报告发送失败")
                return False
                
        except Exception as e:
            logger.error(f"生成和发送报告失败: {e}")
            return False
    
    def run_complete_workflow(self) -> bool:
        """运行完整的工作流程"""
        try:
            logger.info("开始执行完整工作流程")
            
            # 1. 数据收集和分析
            if not self.collect_and_analyze_data():
                return False
            
            # 2. 生成和发送报告
            if not self.generate_and_send_report():
                return False
            
            logger.info("完整工作流程执行成功")
            return True
            
        except Exception as e:
            logger.error(f"完整工作流程执行失败: {e}")
            return False
    
    def get_latest_products(self) -> List[ProductInfo]:
        """获取最新的产品数据"""
        return self.latest_products
    
    def get_latest_report(self) -> Optional[DailyReport]:
        """获取最新的报告"""
        return self.latest_report
    
    def send_test_message(self) -> bool:
        """发送测试消息"""
        return self.feishu_sender.send_test_message()
    
    def send_error_notification(self, error_message: str) -> bool:
        """发送错误通知"""
        return self.feishu_sender.send_error_notification(error_message)
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            "app_name": config.app.name,
            "version": config.app.version,
            "latest_products_count": len(self.latest_products),
            "latest_report_date": self.latest_report.date.isoformat() if self.latest_report else None,
            "feishu_configured": bool(config.feishu.webhook_url or (config.feishu.app_id and config.feishu.app_secret)),
            "ai_configured": bool(config.ai.api_key),
            "timezone": config.app.timezone
        }
    
    def manual_trigger(self, target_date: Optional[datetime] = None) -> bool:
        """手动触发任务执行"""
        try:
            logger.info(f"手动触发任务执行")
            
            if target_date:
                logger.info(f"指定日期: {target_date}")
                # 获取指定日期的数据
                raw_products = self.scraper.get_daily_products(target_date)
            else:
                # 获取今日数据
                raw_products = self.scraper.get_daily_products()
            
            if not raw_products:
                logger.warning("未获取到产品数据")
                return False
            
            # 进行AI分析
            unique_products = self.ai_analyzer.remove_duplicates(raw_products)
            ai_products = self.ai_analyzer.analyze_products(unique_products)
            
            # 生成报告
            analysis_summary = self.ai_analyzer.generate_daily_summary(ai_products)
            report = self.report_generator.generate_daily_report(ai_products, analysis_summary)
            
            # 发送报告
            success = self.feishu_sender.send_daily_report(report)
            
            if success:
                self.latest_products = ai_products
                self.latest_report = report
                logger.info("手动任务执行成功")
                return True
            else:
                logger.error("手动任务执行失败")
                return False
                
        except Exception as e:
            logger.error(f"手动任务执行异常: {e}")
            return False 