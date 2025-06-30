import json
import sys
import os

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

def api(request):
    """Vercel函数处理器"""
    
    # 设置CORS头
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # 处理预检请求
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    # 只处理POST请求
    if request.method != 'POST':
        return (json.dumps({
            "success": False,
            "error": "只支持POST请求"
        }, ensure_ascii=False), 405, headers)
    
    try:
        # 读取请求数据
        body = request.get_data()
        if body:
            request_data = json.loads(body.decode('utf-8'))
        else:
            request_data = {}
        
        action = request_data.get('action', 'generate_report')
        
        if action == 'generate_report':
            # 执行AI日报生成
            result = generate_ai_report()
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
            
    except Exception as e:
        if logger:
            logger.error(f"处理请求时发生错误: {e}")
        response_data = {
            "success": False,
            "error": str(e)
        }
    
    return (json.dumps(response_data, ensure_ascii=False), 200, headers)

def generate_ai_report():
    """生成AI日报"""
    try:
        if logger:
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
        
        if logger:
            logger.info("AI日报生成完成")
        
        return {
            "products_count": len(result.get("products", [])),
            "report_files": result.get("report_files", []),
            "feishu_sent": result.get("feishu_sent", False)
        }
        
    except Exception as e:
        if logger:
            logger.error(f"生成AI日报失败: {e}")
        raise e 