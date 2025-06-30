# Vercel Python Runtime
import json
import sys
import os
from http.server import BaseHTTPRequestHandler

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)
sys.path.insert(0, parent_dir)

try:
    from src.main_service import RainbowOneService
    from src.config import config
    import logging
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
except ImportError as e:
    print(f"Import error: {e}")
    logger = None

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # 设置CORS头
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if content_length > 0:
                request_data = json.loads(post_data.decode('utf-8'))
            else:
                request_data = {}
            
            action = request_data.get('action', 'generate_report')
            
            if action == 'generate_report':
                # 执行AI日报生成
                result = self.generate_ai_report()
                response = {
                    "success": True,
                    "message": "AI日报生成成功！已推送到飞书",
                    "data": result
                }
            else:
                response = {
                    "success": False,
                    "error": "未知的操作类型"
                }
                
        except Exception as e:
            logger.error(f"处理请求时发生错误: {e}")
            response = {
                "success": False,
                "error": str(e)
            }
        
        # 发送响应
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        # 处理预检请求
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def generate_ai_report(self):
        """生成AI日报"""
        try:
            logger.info("开始生成AI日报...")
            
            # 创建主服务实例
            rainbow_service = RainbowOneService()
            
            # 执行完整的工作流程
            success = rainbow_service.run_complete_workflow()
            
            if not success:
                raise Exception("工作流程执行失败")
            
            # 获取结果
            products = rainbow_service.get_latest_products()
            report = rainbow_service.get_latest_report()
            
            result = {
                "products": [{"name": p.name, "ranking": p.ranking} for p in products],
                "report_date": report.date.isoformat() if report else None,
                "feishu_sent": success
            }
            
            logger.info("AI日报生成完成")
            
            return {
                "products_count": len(result.get("products", [])),
                "report_files": result.get("report_files", []),
                "feishu_sent": result.get("feishu_sent", False)
            }
            
        except Exception as e:
            logger.error(f"生成AI日报失败: {e}")
            raise e 