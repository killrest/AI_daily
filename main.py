#!/usr/bin/env python3
"""
彩虹一号 AI 日报系统
主程序入口

使用方法:
python main.py --mode scheduler  # 启动定时任务模式
python main.py --mode once       # 执行一次完整任务
python main.py --mode test       # 发送测试消息
python main.py --mode status     # 查看系统状态
"""

import argparse
import logging
import sys
import os
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.scheduler import TaskScheduler
from src.main_service import RainbowOneService
from src.config import config

def setup_logging():
    """配置日志系统"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, config.app.log_level.upper(), logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler('rainbow_one.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 设置第三方库的日志级别
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)

def run_scheduler():
    """运行定时任务模式"""
    print("🌈 启动彩虹一号 AI 日报系统 - 定时任务模式")
    
    scheduler = TaskScheduler()
    
    try:
        # 设置定时任务
        scheduler.setup_schedules()
        
        # 发送启动通知
        scheduler.send_startup_notification()
        
        # 启动调度器
        scheduler.start()
        
    except KeyboardInterrupt:
        print("\n收到停止信号，正在关闭系统...")
        scheduler.stop()
    except Exception as e:
        print(f"系统异常: {e}")
        logging.error(f"系统异常: {e}")

def run_once():
    """执行一次完整任务"""
    print("🌈 执行一次完整的彩虹一号任务")
    
    service = RainbowOneService()
    success = service.run_complete_workflow()
    
    if success:
        print("✅ 任务执行成功")
        return 0
    else:
        print("❌ 任务执行失败")
        return 1

def send_test():
    """发送测试消息"""
    print("🌈 发送测试消息到飞书")
    
    service = RainbowOneService()
    success = service.send_test_message()
    
    if success:
        print("✅ 测试消息发送成功")
        return 0
    else:
        print("❌ 测试消息发送失败，请检查飞书配置")
        return 1

def show_status():
    """显示系统状态"""
    print("🌈 彩虹一号系统状态")
    
    service = RainbowOneService()
    status = service.get_status()
    
    print(f"应用名称: {status['app_name']}")
    print(f"版本: {status['version']}")
    print(f"时区: {status['timezone']}")
    print(f"最新产品数量: {status['latest_products_count']}")
    print(f"最新报告日期: {status['latest_report_date'] or '无'}")
    print(f"飞书配置: {'✅ 已配置' if status['feishu_configured'] else '❌ 未配置'}")
    print(f"AI配置: {'✅ 已配置' if status['ai_configured'] else '❌ 未配置'}")
    
    return 0

def check_config():
    """检查配置文件"""
    print("🔧 检查配置文件...")
    
    issues = []
    
    # 检查AI配置 - 根据provider检查不同的API密钥
    if config.ai.provider == 'volcengine_ark':
        if not config.ai.api_key:
            issues.append("❌ 火山引擎ARK API密钥未配置 (VOLCENGINE_ARK_API_KEY)")
    elif config.ai.provider == 'openai':
        if not config.ai.api_key:
            issues.append("❌ OpenAI API密钥未配置 (OPENAI_API_KEY)")
    else:
        issues.append(f"❌ 不支持的AI提供商: {config.ai.provider}")
    
    # 检查飞书配置
    if not config.feishu.webhook_url and not (config.feishu.app_id and config.feishu.app_secret):
        issues.append("❌ 飞书配置不完整 (需要FEISHU_WEBHOOK_URL 或 FEISHU_APP_ID+FEISHU_APP_SECRET)")
    
    if issues:
        print("配置检查发现问题:")
        for issue in issues:
            print(f"  {issue}")
        print("\n请参考 env_config.txt 文件配置环境变量")
        return False
    else:
        print("✅ 配置检查通过")
        print(f"✅ AI提供商: {config.ai.provider}")
        print(f"✅ AI模型: {config.ai.model}")
        if config.ai.provider == 'volcengine_ark':
            print(f"✅ ARK端点: {config.ai.endpoint_id}")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="彩虹一号 AI 日报系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
运行模式说明:
  scheduler    启动定时任务模式，按配置的时间自动执行
  once         立即执行一次完整的数据收集和报告生成
  test         发送测试消息到飞书
  status       显示系统当前状态
  config       检查配置文件

示例:
  python main.py --mode scheduler
  python main.py --mode once
  python main.py --mode test
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['scheduler', 'once', 'test', 'status', 'config'],
        default='scheduler',
        help='运行模式 (默认: scheduler)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='启用详细日志输出'
    )
    
    args = parser.parse_args()
    
    # 设置日志
    if args.verbose:
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    setup_logging()
    
    # 显示启动信息
    print(f"🌈 彩虹一号 AI 日报系统 v{config.app.version}")
    print(f"运行模式: {args.mode}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    try:
        if args.mode == 'config':
            return 0 if check_config() else 1
        
        # 检查基本配置
        if not check_config():
            return 1
        
        if args.mode == 'scheduler':
            run_scheduler()
            return 0
        elif args.mode == 'once':
            return run_once()
        elif args.mode == 'test':
            return send_test()
        elif args.mode == 'status':
            return show_status()
        else:
            parser.print_help()
            return 1
            
    except Exception as e:
        print(f"程序执行异常: {e}")
        logging.error(f"程序执行异常: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 