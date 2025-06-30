import json

def handler(request):
    """Vercel健康检查函数处理器"""
    
    # 设置CORS头
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }
    
    # 处理预检请求
    if request.method == 'OPTIONS':
        return ('', 200, headers)
    
    # 健康检查响应
    response_data = {
        "success": True,
        "message": "服务运行正常",
        "service": "彩虹一号 AI 日报生成器",
        "version": "1.0.0"
    }
    
    return (json.dumps(response_data, ensure_ascii=False), 200, headers) 