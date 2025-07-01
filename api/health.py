import json
from http import HTTPStatus

def handler(request):
    """健康检查处理函数"""
    # 健康检查响应
    response_data = {
        "success": True,
        "message": "服务运行正常",
        "service": "彩虹一号 AI 日报生成器",
        "version": "1.0.0"
    }
    
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json; charset=utf-8',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        },
        'body': json.dumps(response_data, ensure_ascii=False)
    } 