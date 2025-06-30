"""
AI 分析器
负责分析产品的AI相关性、翻译内容和生成详细分析
支持火山引擎ARK平台的DeepSeek-V3模型
"""

import requests
import json
import logging
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

from .models import ProductInfo, DailyReport
from .config import config

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """AI分析器 - 支持火山引擎ARK平台"""
    
    def __init__(self):
        self.provider = config.ai.provider
        self.model = config.ai.model
        self.temperature = config.ai.temperature
        self.max_tokens = config.ai.max_tokens
        self.api_key = config.ai.api_key
        self.base_url = config.ai.base_url
        self.endpoint_id = config.ai.endpoint_id
        
        if self.provider == 'volcengine_ark':
            self.api_url = f"{self.base_url}/chat/completions"
        else:
            # 保持对OpenAI的兼容性
            import openai
            openai.api_key = self.api_key
        
    def _call_volcengine_ark_api(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        """调用火山引擎ARK平台API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.endpoint_id,  # 使用endpoint_id作为model参数
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"火山引擎ARK API返回格式异常: {result}")
                return ""
                
        except requests.exceptions.RequestException as e:
            logger.error(f"火山引擎ARK API请求失败: {e}")
            return ""
        except Exception as e:
            logger.error(f"火山引擎ARK API调用异常: {e}")
            return ""
    
    def _call_openai_api(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        """调用OpenAI API（保持兼容性）"""
        try:
            import openai
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API调用失败: {e}")
            return ""
    
    def _call_ai_api(self, messages: List[Dict], temperature: float = None, max_tokens: int = None) -> str:
        """统一的AI API调用接口"""
        if self.provider == 'volcengine_ark':
            return self._call_volcengine_ark_api(messages, temperature, max_tokens)
        else:
            return self._call_openai_api(messages, temperature, max_tokens)
        
    def analyze_products(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """
        批量分析产品列表，提高效率并减少API调用次数
        """
        if not products:
            return []
        
        logger.info(f"开始批量分析 {len(products)} 个产品...")
        
        try:
            # 批量分析所有产品
            analyzed_products = self._batch_analyze_products(products)
            
            logger.info(f"批量分析完成，成功分析 {len(analyzed_products)} 个产品")
            return analyzed_products
            
        except Exception as e:
            logger.error(f"批量分析失败，回退到单个分析: {e}")
            # 如果批量分析失败，回退到原来的单个分析方式
            return self._fallback_single_analysis(products)
    
    def _batch_analyze_products(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """批量分析多个产品"""
        # 构建批量分析的输入数据
        products_data = []
        for i, product in enumerate(products, 1):
            product_data = {
                "index": i,
                "name": product.name,
                "tagline": product.tagline,
                "description": product.description,
                "tags": product.tags,
                "maker_comment": product.maker_comment or "无"
            }
            products_data.append(product_data)
        
        # 构建批量分析的提示词
        prompt = self._build_batch_analysis_prompt(products_data)
        
        # 调用AI API进行批量分析
        messages = [{"role": "user", "content": prompt}]
        response = self._call_ai_api(messages, temperature=0.1, max_tokens=8000)
        
        if not response:
            raise Exception("AI批量分析返回空结果")
        
        # 解析批量分析结果
        analyzed_products = self._parse_batch_analysis_result(response, products)
        
        return analyzed_products
    
    def _build_batch_analysis_prompt(self, products_data: list) -> str:
        """构建批量分析的提示词"""
        products_text = ""
        for product in products_data:
            products_text += f"""
产品 {product['index']}:
- 名称: {product['name']}
- 标语: {product['tagline']}
- 描述: {product['description']}
- 标签: {', '.join(product['tags']) if product['tags'] else '无'}
- 创始人评论: {product['maker_comment']}
"""
        
        prompt = f"""请对以下 {len(products_data)} 个Product Hunt产品进行批量分析。

{products_text}

请严格按照以下JSON格式返回分析结果，每个产品一个对象：

{{
  "products": [
    {{
      "index": 1,
      "ai_relevance_score": 0.8,
      "translated_description": "中文翻译的产品描述",
      "application_scenarios": ["场景1", "场景2", "场景3"],
      "founder_insights": "创始人洞察分析"
    }},
    {{
      "index": 2,
      "ai_relevance_score": 0.2,
      "translated_description": "中文翻译的产品描述",
      "application_scenarios": ["场景1", "场景2", "场景3"],
      "founder_insights": "创始人洞察分析"
    }}
  ]
}}

分析要求：
1. ai_relevance_score: 0-1之间的AI相关性评分
   - 0.9-1.0: 核心AI产品（AI模型、机器学习平台、智能助手等）
   - 0.7-0.8: 重度使用AI技术（AI生成内容、智能分析等）
   - 0.5-0.6: 轻度使用AI功能（部分AI功能、智能推荐等）
   - 0.3-0.4: 间接相关（AI训练数据、开发工具等）
   - 0.0-0.2: 不相关或仅提及AI概念

2. translated_description: 将产品描述翻译成中文，保持专业性和准确性

3. application_scenarios: 列出3个具体应用场景，每个场景15字以内，贴合产品实际功能

4. founder_insights: 如果有创始人评论，分析创始人的动机（为什么做这个产品）、要解决的问题、采用的解决方案；如果没有创始人评论则返回"暂无创始人评论信息"

请确保返回有效的JSON格式，不要包含markdown代码块标记。"""
        
        return prompt
    
    def _parse_batch_analysis_result(self, response: str, original_products: List[ProductInfo]) -> List[ProductInfo]:
        """解析批量分析结果"""
        try:
            # 清理可能的markdown标记
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean.replace('```json', '').replace('```', '').strip()
            elif response_clean.startswith('```'):
                response_clean = response_clean.replace('```', '').strip()
            
            logger.debug(f"批量分析响应: {response_clean[:300]}...")
            
            # 解析JSON
            analysis_result = json.loads(response_clean)
            
            if 'products' not in analysis_result:
                raise Exception("批量分析结果格式错误：缺少products字段")
            
            analyzed_products = []
            products_analysis = analysis_result['products']
            
            # 按照索引匹配原始产品和分析结果
            for analysis in products_analysis:
                index = analysis.get('index', 0) - 1  # 转换为0基索引
                
                if 0 <= index < len(original_products):
                    product = original_products[index]
                    
                    # 更新产品信息
                    product.ai_relevance_score = analysis.get('ai_relevance_score', 0.0)
                    product.translated_description = analysis.get('translated_description', product.description)
                    product.application_scenarios = analysis.get('application_scenarios', [])
                    product.founder_insights = analysis.get('founder_insights', '暂无创始人评论信息')
                    
                    analyzed_products.append(product)
                    
                    logger.info(f"分析产品: {product.name} (AI相关性: {product.ai_relevance_score:.2f})")
            
            return analyzed_products
            
        except json.JSONDecodeError as e:
            logger.error(f"批量分析JSON解析失败: {e}")
            logger.debug(f"原始响应: {response}")
            raise Exception(f"批量分析结果解析失败: {e}")
        except Exception as e:
            logger.error(f"批量分析结果处理失败: {e}")
            raise
    
    def _fallback_single_analysis(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """回退到单个产品分析的方法"""
        logger.info("使用单个产品分析模式作为备选方案")
        analyzed_products = []
        
        for product in products:
            try:
                # 计算AI相关性评分（仅用于参考，不过滤）
                relevance_score = self._calculate_ai_relevance(product)
                
                # 对所有产品进行详细分析
                analyzed_product = self._analyze_single_product(product)
                analyzed_product.ai_relevance_score = relevance_score
                analyzed_products.append(analyzed_product)
                
                logger.info(f"分析产品: {product.name} (AI相关性: {relevance_score:.2f})")
                    
            except Exception as e:
                logger.error(f"分析产品 {product.name} 失败: {e}")
                continue
                
        return analyzed_products
    
    def _calculate_ai_relevance(self, product: ProductInfo) -> float:
        """计算产品的AI相关性评分"""
        try:
            prompt = f"""请分析以下产品是否与AI/人工智能相关，并给出0-1之间的相关性评分：

产品名称: {product.name}
产品介绍: {product.tagline}
产品描述: {product.description}
产品标签: {', '.join(product.tags)}

评分标准：
- 0.9-1.0: 核心AI产品（如AI模型、机器学习平台、智能助手等）
- 0.7-0.8: 重度使用AI技术的产品（如AI生成内容、智能分析等）
- 0.5-0.6: 轻度使用AI功能的产品（如部分AI功能、智能推荐等）
- 0.3-0.4: 间接相关（如AI训练数据、开发工具等）
- 0.0-0.2: 不相关或仅提及AI概念

请直接返回数字评分，不需要解释。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_ai_api(messages, temperature=0.1, max_tokens=10)
            
            if response:
                # 尝试从响应中提取数字评分
                score_match = re.search(r'(?:^|\s)(0?\.\d+|1\.0|0|1)(?:\s|$)', response)
                if score_match:
                    score = float(score_match.group(1))
                    return max(0.0, min(1.0, score))
            
            return 0.0
            
        except Exception as e:
            logger.error(f"计算AI相关性失败: {e}")
            return 0.0
    
    def _analyze_single_product(self, product: ProductInfo) -> ProductInfo:
        """对单个产品进行详细分析"""
        try:
            prompt = f"""请对以下产品进行分析：

产品名称: {product.name}
产品介绍: {product.tagline}
产品描述: {product.description}
创始人评论: {product.maker_comment or '无'}

请严格按照以下JSON格式返回分析结果，不要添加任何额外文字：

{{
  "translated_description": "中文翻译的产品描述",
  "application_scenarios": ["场景1", "场景2", "场景3"],
  "founder_insights": "创始人洞察分析"
}}

分析要求：
- translated_description: 将产品描述翻译成中文，保持专业性和准确性
- application_scenarios: 列出3个具体应用场景，每个场景15字以内，贴合产品实际功能
- founder_insights: 如果有创始人评论，分析创始人的动机（为什么做这个产品）、要解决的问题、采用的解决方案；如果没有创始人评论则返回"暂无创始人评论信息"

请确保返回有效的JSON格式，不要包含markdown代码块标记。"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_ai_api(messages, temperature=0.1)
            
            if response:
                try:
                    # 清理可能的markdown标记
                    response_clean = response.strip()
                    if response_clean.startswith('```json'):
                        response_clean = response_clean.replace('```json', '').replace('```', '').strip()
                    elif response_clean.startswith('```'):
                        response_clean = response_clean.replace('```', '').strip()
                    
                    logger.debug(f"AI响应: {response_clean[:200]}...")
                    
                    # 尝试解析JSON
                    analysis_result = json.loads(response_clean)
                    
                    # 更新产品信息
                    product.translated_description = analysis_result.get('translated_description', product.description)
                    product.application_scenarios = analysis_result.get('application_scenarios', [])
                    product.founder_insights = analysis_result.get('founder_insights', '暂无创始人评论信息')
                    
                    logger.info(f"AI分析成功: {product.name}")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON解析失败，尝试简单分析: {e}")
                    logger.debug(f"原始响应: {response}")
                    
                    # 如果JSON解析失败，尝试简单处理
                    product.translated_description = self._simple_translate(product.description)
                    product.founder_insights = self._extract_insights_from_text(response, product.maker_comment)
                    
            else:
                logger.warning(f"AI分析失败，使用默认值")
                product.translated_description = self._simple_translate(product.description)
                product.founder_insights = '暂无创始人评论信息'
            
            return product
            
        except Exception as e:
            logger.error(f"AI分析产品失败: {e}")
            # 发生错误时，至少保证基本信息可用
            product.translated_description = self._simple_translate(product.description)
            product.founder_insights = '暂无创始人评论信息'
            return product
    
    def _extract_insights_from_text(self, ai_response: str, maker_comment: str) -> str:
        """从AI响应文本中提取创始人洞察"""
        try:
            if not maker_comment:
                return '暂无创始人评论信息'
            
            # 如果AI响应中包含有用信息，提取关键部分
            if ai_response and len(ai_response) > 20:
                # 简单的关键词提取
                insights = []
                lines = ai_response.split('\n')
                for line in lines:
                    if ('创始人' in line or '解决' in line or '问题' in line or 
                        '动机' in line or '方法' in line or '理念' in line):
                        insights.append(line.strip())
                
                if insights:
                    return ' '.join(insights[:3])  # 最多取3条
            
            # 如果提取失败，返回基本的创始人评论摘要
            if len(maker_comment) > 100:
                return f"创始人分享了产品背景和理念：{maker_comment[:150]}..."
            else:
                return maker_comment
                
        except Exception:
            return '暂无创始人评论信息'
    
    def _simple_translate(self, text: str) -> str:
        """简单翻译功能"""
        if not text:
            return text
            
        try:
            prompt = f"""请将以下英文翻译为中文，要求：
1. 保持原意和专业性
2. 只返回翻译结果，不要包含任何翻译说明、解释或备注
3. 使用简洁自然的中文表达

原文：{text}"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_ai_api(messages, temperature=0.1, max_tokens=1000)
            
            return response if response else text
            
        except Exception as e:
            logger.error(f"翻译失败: {e}")
            return text
    
    def generate_daily_summary(self, products: List[ProductInfo]) -> str:
        """生成每日AI产品趋势总结"""
        if not products:
            return "今日暂无AI相关产品发布。"
            
        try:
            product_list = "\n".join([
                f"{i+1}. {p.name}: {p.tagline}" 
                for i, p in enumerate(products)
            ])
            
            prompt = f"""基于今日Product Hunt上的AI相关产品，请生成一份简洁的趋势分析总结：

今日AI产品列表：
{product_list}

请从以下角度进行分析：
1. 主要趋势和方向
2. 技术特点
3. 应用领域分布
4. 值得关注的亮点"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self._call_ai_api(messages, max_tokens=500)
            
            return response if response else f"今日发现 {len(products)} 个AI相关产品，涵盖多个应用领域。"
            
        except Exception as e:
            logger.error(f"生成每日总结失败: {e}")
            return f"今日发现 {len(products)} 个AI相关产品，涵盖多个应用领域。"
    
    def remove_duplicates(self, products: List[ProductInfo]) -> List[ProductInfo]:
        """去除重复产品"""
        seen_names = set()
        unique_products = []
        
        for product in products:
            # 简单的去重逻辑，基于产品名称
            name_key = product.name.lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                unique_products.append(product)
            else:
                logger.info(f"发现重复产品，已跳过: {product.name}")
                
        return unique_products 