"""
彩虹一号 - 飞书消息推送模块
"""
import os
import json
import time
import hmac
import hashlib
import base64
import logging
import requests
from typing import Optional, Dict, Any, List

from .models import DailyReport

class FeishuSender:
    """飞书消息发送器"""
    
    def __init__(self, webhook_url: str, webhook_secret: Optional[str] = None):
        """
        初始化飞书发送器
        
        Args:
            webhook_url: 飞书机器人Webhook URL
            webhook_secret: 飞书机器人加签密钥（可选）
        """
        self.webhook_url = webhook_url
        self.webhook_secret = webhook_secret
        self.logger = logging.getLogger(__name__)
        
    def _generate_signature(self, timestamp: str) -> str:
        """
        生成飞书加签验证签名
        
        根据飞书官方文档和Java示例，正确的签名算法：
        1. 签名字符串 = timestamp + "\n" + 密钥
        2. 使用签名字符串作为HMAC的key，空字节数组作为消息
        3. Base64编码结果
        
        Args:
            timestamp: 时间戳字符串
            
        Returns:
            签名字符串
        """
        if not self.webhook_secret:
            return ""
        
        # 按照飞书文档：timestamp + "\n" + 密钥
        string_to_sign = f"{timestamp}\n{self.webhook_secret}"
        
        # 关键：使用签名字符串作为key，空字节数组作为消息
        signature = hmac.new(
            string_to_sign.encode("utf-8"),  # 签名字符串作为key
            b'',  # 空字节数组作为消息
            digestmod=hashlib.sha256
        ).digest()
        
        # Base64编码
        return base64.b64encode(signature).decode('utf-8')
    
    def send_text_message(self, content: str) -> bool:
        """
        发送文本消息到飞书群聊
        
        Args:
            content: 消息内容
            
        Returns:
            发送是否成功
        """
        try:
            timestamp = str(int(time.time()))
            
            # 构建消息数据
            data = {
                "msg_type": "text",
                "content": {
                    "text": content
                }
            }
            
            # 如果有加签密钥，添加签名
            if self.webhook_secret:
                signature = self._generate_signature(timestamp)
                data["timestamp"] = timestamp
                data["sign"] = signature
            
            # 发送POST请求
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0 or result.get('code') == 0:
                    self.logger.info("文本消息发送成功")
                    return True
                else:
                    self.logger.error(f"飞书API返回错误: {result}")
                    return False
            else:
                self.logger.error(f"HTTP请求失败: {response.status_code}, {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"发送文本消息失败: {e}")
            return False
    
    def send_test_message(self) -> bool:
        """
        发送测试消息到飞书群聊
        
        Returns:
            发送是否成功
        """
        try:
            test_content = """🌈 彩虹一号 AI 日报系统测试

🔧 **系统状态**: 正常运行
⏰ **测试时间**: 刚刚
✅ **飞书连接**: 成功

这是一条测试消息，用于验证彩虹一号AI日报系统与飞书的连接是否正常。如果您看到这条消息，说明系统配置正确！

---
*彩虹一号 AI 日报系统 v1.0.0*"""
            
            self.logger.info("发送测试消息到飞书...")
            success = self.send_text_message(test_content)
            
            if success:
                self.logger.info("测试消息发送成功")
            else:
                self.logger.error("测试消息发送失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"发送测试消息异常: {e}")
            return False
    
    def send_daily_report(self, report: DailyReport) -> bool:
        """
        发送日报到飞书群聊
        
        Args:
            report: 日报对象
            
        Returns:
            发送是否成功
        """
        try:
            # 生成日报的Markdown内容
            from .report_generator import ReportGenerator
            generator = ReportGenerator()
            markdown_content = generator.format_report_as_markdown(report)
            
            # 直接发送一条完整消息，不分段
            self.logger.info(f"准备发送日报，内容长度: {len(markdown_content)} 字符")
            return self.send_text_message(markdown_content)
            
        except Exception as e:
            self.logger.error(f"发送日报失败: {e}")
            return False
    
    def _send_long_message(self, content: str, max_length: int = 3000) -> bool:
        """
        分段发送长消息
        
        Args:
            content: 消息内容
            max_length: 单段最大长度
            
        Returns:
            发送是否成功
        """
        try:
            if len(content) <= max_length:
                return self.send_text_message(content)
            
            # 按段落分割内容
            paragraphs = content.split('\n\n')
            current_chunk = ""
            all_success = True
            
            for paragraph in paragraphs:
                # 如果当前块加上新段落超过限制，先发送当前块
                if len(current_chunk) + len(paragraph) + 2 > max_length and current_chunk:
                    success = self.send_text_message(current_chunk)
                    if not success:
                        all_success = False
                    current_chunk = paragraph
                    time.sleep(1)  # 避免频率限制
                else:
                    if current_chunk:
                        current_chunk += "\n\n" + paragraph
                    else:
                        current_chunk = paragraph
            
            # 发送最后一块
            if current_chunk:
                success = self.send_text_message(current_chunk)
                if not success:
                    all_success = False
            
            return all_success
            
        except Exception as e:
            self.logger.error(f"分段发送失败: {e}")
            return False 