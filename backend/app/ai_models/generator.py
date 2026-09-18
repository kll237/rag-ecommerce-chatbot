"""
响应生成器
基于模板和大语言模型
"""
from typing import List, Optional
import warnings
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import httpx
import json

from ..config import config

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    warnings.warn("openai未安装")

class ResponseGenerator:
    """响应生成器"""

    # 响应模板（优化版，更详细丰富）
    TEMPLATES = {
        'greeting': """👋 您好！我是您的智能客服助手，非常高兴为您服务！

我可以帮您：
• 📦 查询商品信息和价格
• 🛒 了解订单和物流状态
• 🔄 处理退换货申请
• 💳 咨询支付和配送问题
• 💬 解答其他购物相关问题

请问有什么可以帮您的？您可以发送文字、语音，或者上传商品图片咨询！""",

        'product_inquiry': """📋 根据您的需求，我为您找到以下商品信息：

{context}

💡 温馨提示：
• 商品库存和价格可能随时变动，请以下单时为准
• 满99元即可享受包邮服务
• 如需了解更多详情，可以上传商品图片或继续提问

您还想了解这些商品的哪些信息呢？比如规格、材质、使用说明等。""",

        'order_inquiry': """📦 关于您的订单问题，我为您提供以下服务：

1️⃣ **在线查询**：
   - 登录您的账户，在"我的订单"中查看详细信息
   - 查看实时物流状态和配送进度

2️⃣ **人工客服**：
   - 客服热线：400-xxx-xxxx（工作日9:00-18:00）
   - 在线客服：APP内点击"联系客服"
   - 微信客服：关注官方公众号留言

3️⃣ **常见问题**：
   - 发货后一般1-3天可查看物流信息
   - 配送时间通常为3-7个工作日
   - 如遇节假日可能延迟

您可以提供订单编号，我可以帮您查询更详细的信息！""",

        'complaint': """😔 非常抱歉给您带来不便，我们非常重视您的问题！

🛡️ **我们承诺**：
- 24小时内响应您的投诉
- 3个工作日内给出解决方案
- 如果是我们的责任，会全额退款或补偿

📝 **处理流程**：
1. 请提供订单编号（方便我们快速定位）
2. 详细描述您遇到的问题（时间、地点、具体情况）
3. 上传相关照片或截图作为凭证
4. 我们会在24小时内联系您

⚡ **紧急情况**：
如需立即处理，请直接拨打客服热线：400-xxx-xxxx

感谢您的理解和支持！""",

        'return_exchange': """🔄 关于退换货，我们的政策如下：

✅ **退货条件**：
1. 7天内可无理由退货（不影响二次销售）
2. 商品需保持原包装和标签完整
3. 附件、赠品等需一并退回
4. 特殊商品（如内衣、定制商品）除外

📦 **退货流程**：
1. 在APP中点击"我的订单" → "申请售后"
2. 选择退货原因并上传照片
3. 填写退货地址信息
4. 寄回商品（建议使用顺丰保价）
5. 我们在收到商品后1-2个工作日退款

💡 **温馨提示**：
- 退货运费由卖家承担（质量问题）
- 非质量问题退货需买家承担运费
- 退款原路返回，3-7个工作日到账

如需帮助，请联系客服！""",

        'payment': """💳 我们支持以下支付方式：

✅ **线上支付**：
1. 支付宝（推荐）：支持余额、花呗、银行卡
2. 微信支付：支持余额、零钱、银行卡
3. 银行卡：支持主流银行借记卡/信用卡

🚚 **货到付款**：
- 仅限部分地区（江浙沪、珠三角等）
- 需额外支付5元手续费
- 订单金额不超过5000元

🎁 **优惠活动**：
- 首次下单立减10元
- 满200减20，满500减50
- 会员专享折扣（最高9折）

💡 **安全提示**：
- 所有支付均在安全加密环境下完成
- 请勿将支付密码告知他人
- 如遇支付问题，请联系客服

您还有其他支付相关问题吗？""",

        'shipping': """🚚 关于配送服务，我们的政策如下：

⏰ **发货时间**：
- 正常商品：下单后1-3个工作日发货
- 预售商品：按商品标注时间发货
- 定制商品：7-15个工作日发货

📍 **配送时间**：
- 省内：1-2天送达
- 省外：3-5天送达
- 偏远地区：5-7天送达

📦 **配送范围**：
- 全国大部分地区（除港澳台及偏远地区）
- 支持送货上门、驿站自提、快递柜

🎁 **包邮政策**：
- 满99元包邮
- 会员专享包邮（不限金额）
- 特殊商品除外

📱 **物流查询**：
- 在APP"我的订单"中查看实时物流
- 收到短信提醒可点击链接查询
- 客服可帮您查询配送状态

💡 **温馨提示**：
- 如遇节假日可能延迟配送
- 配送前会提前电话联系
- 请保持手机畅通

您还有其他配送问题吗？""",

        'faq': """📚 根据知识库，我为您找到以下相关信息：

{context}

💡 **需要更多帮助？**
如果您对以上信息有疑问，可以：
- 继续提问，我会尽力解答
- 上传相关图片，我可以帮您识别
- 联系人工客服获得一对一服务

希望以上信息对您有帮助！""",

        'other': """💬 感谢您的提问！

根据相关信息：

{context}

📋 **我还可以帮您**：
• 📦 查询商品信息和价格
• 🛒 了解订单和物流状态
• 🔄 处理退换货申请
• 💳 咨询支付和配送问题

💡 **温馨提示**：
您也可以上传商品图片，我可以帮您识别并提供详细信息！

如果以上回答未能完全解决您的问题，建议您：
1. 提供更多详细信息
2. 上传相关截图或照片
3. 联系人工客服：400-xxx-xxxx

我会继续为您提供帮助！"""
    }

    def __init__(self):
        """初始化响应生成器"""
        # 使用豆包API配置
        self.use_doubao = config.DOUBAO_API_KEY and config.DOUBAO_API_KEY != "your-doubao-api-key"

        if self.use_doubao:
            print(f"[ResponseGenerator] 豆包大模型已配置")
            print(f"[ResponseGenerator] Model: {config.DOUBAO_MODEL}")
            print(f"[ResponseGenerator] Base URL: {config.DOUBAO_BASE_URL}")
        else:
            print(f"[ResponseGenerator] 大模型未配置，将使用模板生成")
            if not config.DOUBAO_API_KEY:
                print(f"[ResponseGenerator] DOUBAO_API_KEY未设置")

    def generate(
        self,
        query: str,
        context: List[str],
        intent: str = 'other'
    ) -> str:
        """
        生成响应（带超时控制和降级机制）

        Args:
            query: 用户查询
            context: 检索到的上下文文档
            intent: 用户意图

        Returns:
            生成的响应文本
        """
        # 如果配置了豆包API，使用大模型生成
        if self.use_doubao:
            try:
                print(f"[ResponseGenerator] 尝试使用大模型生成响应...")
                # 使用线程池控制超时
                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(
                        self._generate_with_llm,
                        query, context, intent
                    )
                    try:
                        # 设置15秒超时
                        response = future.result(timeout=15)
                        print(f"[ResponseGenerator] ✅ 大模型生成成功")
                        return response
                    except FutureTimeoutError:
                        print(f"[ResponseGenerator] ⚠️ 大模型调用超时（15秒），降级到模板")
                        future.cancel()
                        return self._generate_with_template(context, intent)
            except Exception as e:
                print(f"[ResponseGenerator] ❌ 大模型调用失败: {e}，降级到模板")
                return self._generate_with_template(context, intent)

        # 否则使用模板
        print(f"[ResponseGenerator] 使用模板生成响应")
        return self._generate_with_template(context, intent)

    def _generate_with_llm(
        self,
        query: str,
        context: List[str],
        intent: str
    ) -> str:
        """使用大语言模型生成响应"""
        # 构建提示词
        context_text = "\n".join([f"- {doc[:150]}..." if len(doc) > 150 else f"- {doc}" for doc in context])

        prompt = f"""你是一个专业的电商客服助手。请根据以下上下文信息回答用户的问题。

用户问题：{query}

相关上下文：
{context_text}

要求：
1. 回答要专业、礼貌、友好
2. 基于提供的上下文信息回答
3. 如果上下文信息不足，诚实地说明
4. 回答要简洁明了，不超过150字
5. 使用emoji让回答更生动

回答："""

        try:
            print(f"[ResponseGenerator] 调用豆包大模型 API: {config.DOUBAO_MODEL}")

            # 使用httpx直接调用豆包API
            url = f"{config.DOUBAO_BASE_URL}/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.DOUBAO_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": config.DOUBAO_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一个专业的电商客服助手，回答要友好、专业、简洁。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 200,
                "temperature": 0.7
            }

            response = httpx.post(url, headers=headers, json=data, timeout=10.0)
            response.raise_for_status()

            result_data = response.json()
            result = result_data["choices"][0]["message"]["content"].strip()

            print(f"[ResponseGenerator] 豆包大模型返回: {result[:50]}...")
            return result

        except httpx.HTTPError as e:
            print(f"[ResponseGenerator] 豆包大模型调用HTTP异常: {type(e).__name__}: {e}")
            raise
        except Exception as e:
            print(f"[ResponseGenerator] 豆包大模型调用异常: {type(e).__name__}: {e}")
            raise

    def _generate_with_template(
        self,
        context: List[str],
        intent: str
    ) -> str:
        """使用模板生成响应"""
        # 如果有检索到的上下文，优先使用上下文生成答案
        if context and intent in ['faq', 'other', 'order_inquiry']:
            # 从上下文中提取最相关的内容
            relevant_info = self._extract_relevant_info(context, intent)
            return relevant_info

        # 获取模板
        template = self.TEMPLATES.get(intent, self.TEMPLATES['other'])

        # 格式化上下文
        context_text = ""
        if context:
            context_text = "\n".join([f"• {doc[:100]}..." if len(doc) > 100 else f"• {doc}" for doc in context[:3]])

        # 替换占位符
        response = template.replace("{context}", context_text if context_text else "暂无相关信息")

        return response

    def _extract_relevant_info(self, context: List[str], intent: str) -> str:
        """从上下文中提取相关信息"""
        # 获取前3个最相关的文档
        docs = context[:3]

        # 尝试提取问答格式的内容
        extracted_answers = []
        for doc in docs:
            # 检查是否包含问答格式
            if 'Q:' in doc and 'A:' in doc:
                # 提取问题后的答案部分
                parts = doc.split('A:')
                if len(parts) > 1:
                    answer = parts[1].strip()
                    # 如果答案很长，只取前500字
                    if len(answer) > 500:
                        answer = answer[:500] + "..."
                    extracted_answers.append(answer)

        # 如果找到了QA格式答案，组合返回
        if extracted_answers:
            combined = "\n\n".join(extracted_answers)
            # 添加总结
            result = f"📚 **相关答案**\n\n{combined}\n\n💡 如需了解更多细节，可以继续提问！"
            return result

        # 如果没有找到QA格式，返回最相关的文档
        if docs:
            best_doc = docs[0]
            # 添加商品信息的额外提示
            if intent == 'product_inquiry':
                result = f"📦 **商品信息**\n\n{best_doc}\n\n💡 您还想了解这个商品的哪些信息？我可以帮您查询规格、材质、价格等详情！"
            else:
                # 限制长度
                if len(best_doc) > 300:
                    best_doc = best_doc[:300] + "..."
                result = f"📝 **相关信息**\n\n{best_doc}\n\n💡 如需更多帮助，请继续提问或联系人工客服。"
            return result

        return """🤔 抱歉，我没有在知识库中找到完全匹配的信息。

💡 **您可以尝试**：
• 换个方式描述您的问题
• 提供更多细节（如订单号、商品名称）
• 上传商品图片，我可以帮您识别

📞 **需要人工帮助？**
- 客服热线：400-xxx-xxxx
- 在线客服：APP内"我的" → "联系客服"
- 工作时间：9:00-18:00

我会继续为您提供帮助！"""