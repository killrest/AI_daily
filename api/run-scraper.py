def handler(request):
    """处理请求的主函数"""
    import json
    import sys
    import os
    import logging
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # 添加src目录到Python路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        src_dir = os.path.join(parent_dir, 'src')
        sys.path.insert(0, src_dir)
        sys.path.insert(0, parent_dir)
        
        # 处理预检请求
        method = getattr(request, 'method', 'GET')
        if method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type',
                },
                'body': ''
            }
        
        # 只处理POST请求
        if method != 'POST':
            return {
                'statusCode': 405,
                'headers': {
                    'Content-Type': 'application/json; charset=utf-8',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    "success": False,
                    "error": "只支持POST请求"
                }, ensure_ascii=False)
            }
        
        # 读取请求数据
        try:
            body = request.get_data() if hasattr(request, 'get_data') else b''
            if body:
                request_data = json.loads(body.decode('utf-8'))
            else:
                request_data = {}
            
            action = request_data.get('action', 'generate_report')
            
            if action == 'generate_report':
                # 执行AI日报生成
                result = generate_ai_report(logger)
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
            logger.error(f"处理请求时发生错误: {e}")
            response_data = {
                "success": False,
                "error": str(e)
            }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            },
            'body': json.dumps(response_data, ensure_ascii=False)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                "success": False,
                "error": f"服务器内部错误: {str(e)}"
            }, ensure_ascii=False)
        }

def generate_ai_report(logger):
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