from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import logging
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """处理POST请求"""
        try:
            # 配置日志
            logging.basicConfig(level=logging.INFO)
            logger = logging.getLogger(__name__)
            
            # 添加src目录到Python路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            parent_dir = os.path.dirname(current_dir)
            src_dir = os.path.join(parent_dir, 'src')
            sys.path.insert(0, src_dir)
            sys.path.insert(0, parent_dir)
            
            # 读取请求数据
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                request_body = self.rfile.read(content_length).decode('utf-8')
                request_data = json.loads(request_body)
            else:
                request_data = {}
            
            action = request_data.get('action', 'generate_report')
            
            if action == 'generate_report':
                # 执行AI日报生成
                result = self.generate_ai_report(logger)
                response_data = {
                    "success": True,
                    "message": "AI日报生成成功！已推送到飞书",
                    "data": result
                }
            else:
                response_data = {
                    "success": False,
                    "error": "未知的操作类型"
                }
            
            # 发送成功响应
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            # 发送错误响应
            error_data = {
                "success": False,
                "error": f"服务器内部错误: {str(e)}"
            }
            
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """处理GET请求 - 不支持"""
        response_data = {
            "success": False,
            "error": "只支持POST请求"
        }
        
        self.send_response(405)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode('utf-8'))
    
    def generate_ai_report(self, logger):
        """生成AI日报"""
        try:
            logger.info("开始生成AI日报...")
            
            # 尝试导入必要模块
            try:
                from src.main_service import RainbowOneService
                logger.info("成功导入 RainbowOneService")
            except ImportError as e:
                logger.error(f"无法导入 RainbowOneService: {e}")
                raise Exception(f"系统模块导入失败: {e}")
            
            # 创建主服务实例
            rainbow_service = RainbowOneService()
            
            # 执行完整的工作流程
            success = rainbow_service.run_complete_workflow()
            
            if not success:
                raise Exception("工作流程执行失败")
            
            # 获取结果
            products = rainbow_service.get_latest_products()
            report = rainbow_service.get_latest_report()
            
            logger.info("AI日报生成完成")
            
            return {
                "products_count": len(products) if products else 0,
                "report_date": report.date.isoformat() if report else None,
                "feishu_sent": success
            }
            
        except Exception as e:
            logger.error(f"生成AI日报失败: {e}")
            raise e 