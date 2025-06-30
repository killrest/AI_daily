"""
定时任务调度器
负责定时执行彩虹一号的各项任务
"""

import schedule
import time
import logging
from datetime import datetime, timezone
import pytz
from typing import Optional

from .config import config
from .main_service import RainbowOneService

logger = logging.getLogger(__name__)

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self):
        self.service = RainbowOneService()
        self.timezone = pytz.timezone(config.app.timezone)
        self.is_running = False
        
    def setup_schedules(self):
        """设置定时任务"""
        # 每日数据收集任务
        data_collection_time = config.schedule.data_collection_time
        schedule.every().day.at(data_collection_time).do(self._run_data_collection)
        
        # 每日报告生成和发送任务
        report_time = config.schedule.daily_report_time
        schedule.every().day.at(report_time).do(self._run_daily_report)
        
        # 每小时系统健康检查（可选）
        schedule.every().hour.do(self._health_check)
        
        logger.info(f"定时任务已设置:")
        logger.info(f"- 数据收集时间: 每日 {data_collection_time}")
        logger.info(f"- 报告发送时间: 每日 {report_time}")
        logger.info(f"- 健康检查: 每小时执行")
    
    def _run_data_collection(self):
        """执行数据收集任务"""
        try:
            logger.info("开始执行每日数据收集任务")
            current_time = datetime.now(self.timezone)
            
            # 执行数据收集和分析
            success = self.service.collect_and_analyze_data()
            
            if success:
                logger.info("每日数据收集任务完成")
            else:
                logger.error("每日数据收集任务失败")
                self.service.send_error_notification("数据收集任务执行失败")
                
        except Exception as e:
            logger.error(f"数据收集任务异常: {e}")
            self.service.send_error_notification(f"数据收集任务异常: {str(e)}")
    
    def _run_daily_report(self):
        """执行每日报告生成和发送任务"""
        try:
            logger.info("开始执行每日报告任务")
            
            # 生成并发送日报
            success = self.service.generate_and_send_report()
            
            if success:
                logger.info("每日报告任务完成")
            else:
                logger.error("每日报告任务失败")
                self.service.send_error_notification("日报生成或发送失败")
                
        except Exception as e:
            logger.error(f"每日报告任务异常: {e}")
            self.service.send_error_notification(f"日报任务异常: {str(e)}")
    
    def _health_check(self):
        """系统健康检查"""
        try:
            logger.debug("执行系统健康检查")
            
            # 检查配置
            if not config.ai.api_key:
                logger.warning("AI API密钥未配置")
            
            if not config.feishu.webhook_url:
                logger.warning("飞书Webhook URL未配置")
            
            # 其他健康检查...
            
        except Exception as e:
            logger.error(f"健康检查异常: {e}")
    
    def run_once(self):
        """立即执行一次完整的数据收集和报告生成"""
        try:
            logger.info("手动执行一次完整任务")
            
            # 数据收集
            self._run_data_collection()
            
            # 等待一段时间确保数据处理完成
            time.sleep(5)
            
            # 生成报告
            self._run_daily_report()
            
            logger.info("手动任务执行完成")
            return True
            
        except Exception as e:
            logger.error(f"手动任务执行失败: {e}")
            return False
    
    def start(self):
        """启动调度器"""
        logger.info("彩虹一号任务调度器启动")
        self.is_running = True
        
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            logger.info("收到停止信号")
        except Exception as e:
            logger.error(f"调度器异常: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止调度器"""
        logger.info("彩虹一号任务调度器停止")
        self.is_running = False
        schedule.clear()
    
    def get_next_run_time(self) -> Optional[str]:
        """获取下次运行时间"""
        try:
            jobs = schedule.get_jobs()
            if jobs:
                next_job = min(jobs, key=lambda job: job.next_run)
                return next_job.next_run.strftime('%Y-%m-%d %H:%M:%S')
            return None
        except Exception as e:
            logger.error(f"获取下次运行时间失败: {e}")
            return None
    
    def list_scheduled_jobs(self):
        """列出所有定时任务"""
        jobs = schedule.get_jobs()
        if not jobs:
            logger.info("当前没有定时任务")
            return
        
        logger.info("当前定时任务列表:")
        for i, job in enumerate(jobs, 1):
            logger.info(f"{i}. {job.job_func.__name__} - 下次运行: {job.next_run}")
    
    def send_startup_notification(self):
        """发送启动通知"""
        try:
            next_run = self.get_next_run_time()
            message = f"🌈 彩虹一号 AI 日报系统已启动\n\n"
            message += f"⏰ 数据收集时间: 每日 {config.schedule.data_collection_time}\n"
            message += f"📊 报告发送时间: 每日 {config.schedule.daily_report_time}\n"
            if next_run:
                message += f"⏳ 下次运行时间: {next_run}\n"
            message += f"\n系统将自动监控 Product Hunt 的 AI 相关产品并生成日报。"
            
            # 通过飞书发送启动通知
            from .feishu_sender import FeishuSender
            sender = FeishuSender()
            return sender.send_test_message()
            
        except Exception as e:
            logger.error(f"发送启动通知失败: {e}")
            return False 