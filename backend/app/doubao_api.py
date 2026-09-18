"""
豆包API客户端
提供语音识别(ASR)、多模态图片识别和语音合成功能
"""
import httpx
import json
from typing import Optional, Dict, Any
from .config import config
import base64
import os
import hashlib


class DoubaoASRClient:
    """豆包语音识别客户端（已废弃，使用Whisper本地模型）"""

    # 推荐使用豆包多模态视觉模型，支持音频输入
    # 该模型专门为音频/视频理解设计，识别准确度高
    ASR_MODEL = config.DOUBAO_ASR_MODEL

    def __init__(self):
        self.api_key = config.DOUBAO_API_KEY
        self.base_url = config.DOUBAO_BASE_URL

    async def recognize(self, audio_data: str, uid: str = "default") -> Dict[str, Any]:
        """
        语音识别（音频转文字）

        使用Whisper本地模型进行语音识别
        如果Whisper不可用，使用演示模式

        Args:
            audio_data: base64编码的音频数据
            uid: 用户ID

        Returns:
            包含识别结果的字典
        """
        # 使用Whisper进行语音识别
        print(f"[DEBUG] 尝试使用Whisper进行语音识别")
        try:
            return await self._recognize_with_whisper(audio_data, uid)
        except Exception as e:
            # Whisper识别失败，使用演示模式
            print(f"[DEBUG] Whisper识别失败: {type(e).__name__}: {str(e)}")
            print(f"[DEBUG] 降级到演示模式")
            return self._demo_mode(f"Whisper识别失败: {str(e)}")

    async def _recognize_with_whisper(self, audio_data: str, uid: str) -> Dict[str, Any]:
        """
        使用Whisper模型进行语音识别（后备方案）

        如果豆包API不可用，使用本地Whisper模型
        """
        print(f"[DEBUG] 尝试使用Whisper进行语音识别")
        try:
            import whisper

            # 将base64音频数据解码为字节
            audio_bytes = base64.b64decode(audio_data)

            # 创建临时音频文件（兼容Windows和Linux）
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_audio_path = os.path.join(temp_dir, f"audio_{uid}.wav")

            print(f"[DEBUG] 临时音频文件路径: {temp_audio_path}")

            # 将音频数据写入临时文件
            with open(temp_audio_path, "wb") as f:
                f.write(audio_bytes)

            # 加载Whisper模型（使用base模型，速度快）
            print(f"[DEBUG] 正在加载Whisper模型...")
            model = whisper.load_model("base")

            # 进行语音识别
            print(f"[DEBUG] 开始Whisper识别...")
            result = model.transcribe(temp_audio_path)

            # 删除临时文件
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
                print(f"[DEBUG] 已删除临时文件")

            print(f"[DEBUG] Whisper识别成功: {result['text']}")
            # 返回识别结果
            return {
                "text": result["text"].strip(),
                "duration": result.get("segments", [{}])[0].get("end", 0) if result.get("segments") else 0,
                "model": "whisper-base",
                "method": "whisper"
            }

        except ImportError:
            # 如果没有安装whisper，使用演示模式
            print(f"[DEBUG] Whisper未安装，降级到演示模式")
            return self._demo_mode("未安装openai-whisper包")

        except Exception as e:
            # 如果Whisper识别失败，使用演示模式
            print(f"[DEBUG] Whisper识别失败: {type(e).__name__}: {str(e)}")
            return self._demo_mode(f"Whisper识别失败: {str(e)}")

    def _demo_mode(self, error_reason: str) -> Dict[str, Any]:
        """
        演示模式：返回模拟的语音识别结果

        不需要下载任何东西，纯模拟返回
        """
        # 模拟的一些常见问题示例
        demo_texts = [
            "你好，我想查询一下我的订单状态",
            "请问这个商品有货吗？",
            "我想退货，应该怎么操作？",
            "这个商品多少钱？",
            "你好，请问运费是多少钱？",
            "我想要推荐一些商品",
            "这个商品有优惠券吗？",
            "请问你们支持哪种支付方式？"
        ]

        # 随机选择一个模拟文本（根据error_reason固定选择，保持一致性）
        text_index = int(hashlib.md5(error_reason.encode()).hexdigest(), 16) % len(demo_texts)
        demo_text = demo_texts[text_index]

        return {
            "text": f"[演示模式] {demo_text}",
            "duration": 3.5,  # 模拟3.5秒的音频时长
            "model": "demo",
            "method": "demo",
            "note": f"当前为演示模式，原因：{error_reason}。请安装 openai-whisper 包: pip install openai-whisper"
        }


class DoubaoVisionClient:
    """豆包多模态视觉客户端"""

    def __init__(self):
        self.api_key = config.DOUBAO_API_KEY
        self.base_url = config.DOUBAO_BASE_URL
        # 使用视觉模型进行图片识别
        self.model = config.DOUBAO_VISION_MODEL

    async def recognize_image(self, image_data: str, question: str = "请识别这张图片中的商品") -> str:
        """
        图片识别（识别商品信息）

        Args:
            image_data: base64编码的图片数据
            question: 提问文本

        Returns:
            识别结果文本
        """
        # 检查API Key配置
        if not self.api_key or self.api_key == "your-doubao-api-key":
            return "（演示模式）图片识别功能需要配置豆包API Key。请在.env文件中设置DOUBAO_API_KEY"

        # 豆包多模态大模型API端点
        url = f"{self.base_url}/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建识别提示词
        system_prompt = """你是一个专业的商品识别助手。请分析用户上传的图片，识别其中的商品信息。

请按以下格式返回结果（必须是中文）：

商品名称：[商品的完整名称]
类别：[商品所属类别，如：手机数码、服装、食品等]
描述：[商品的特点、功能、外观等详细描述]
特征：[列出3-5个关键特征，用顿号分隔]
建议价格：[根据商品质量给出合理的价格范围，格式：¥xxx-xxx]

注意：
1. 只识别商品相关内容
2. 如果图片中没有商品，请明确说明
3. 价格范围要合理
4. 特征要具体、准确"""

        # 构建消息（包含图片和文本）
        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            }
        ]

        # 构建请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()

                # 解析API返回结果
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    return "无法识别图片内容"

        except httpx.HTTPError as e:
            # 返回友好的提示信息，避免前端崩溃
            return f"（演示模式）图片识别API调用失败：{str(e)}。请检查网络连接或API配置。"


class DoubaoTTSClient:
    """豆包语音合成客户端（TTS - Text-to-Speech）"""

    def __init__(self):
        self.api_key = config.DOUBAO_API_KEY
        self.base_url = config.DOUBAO_BASE_URL

    async def synthesize(
        self,
        text: str,
        uid: str = "default",
        speaker: str = "zh_female_xiaohe_uranus_bigtts",
        audio_format: str = "mp3",
        sample_rate: int = 24000,
        speech_rate: int = 0,
        loudness_rate: int = 0
    ) -> Dict[str, Any]:
        """
        文本转语音

        Args:
            text: 要合成的文本
            uid: 用户ID
            speaker: 音色ID，默认为女性声音
            audio_format: 音频格式（mp3/pcm/ogg_opus）
            sample_rate: 采样率（8000-48000）
            speech_rate: 语速调整（-50到100）
            loudness_rate: 音量调整（-50到100）

        Returns:
            包含音频数据的字典
        """
        # 检查API Key配置
        if not self.api_key or self.api_key == "your-doubao-api-key":
            print(f"[DEBUG] 未配置豆包API Key，使用演示模式")
            return self._demo_mode("未配置豆包API Key")

        try:
            print(f"[DEBUG] 开始TTS语音合成，文本长度: {len(text)}")

            # 调用语音合成API
            url = f"{self.base_url}/tts/unidirectional"

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Connection": "keep-alive"
            }

            # 构建请求数据
            data = {
                "user": {
                    "uid": uid
                },
                "req_params": {
                    "text": text,
                    "speaker": speaker,
                    "audio_params": {
                        "format": audio_format,
                        "sample_rate": sample_rate,
                        "speech_rate": speech_rate,
                        "loudness_rate": loudness_rate
                    }
                }
            }

            print(f"[DEBUG] TTS请求参数: speaker={speaker}, format={audio_format}, sample_rate={sample_rate}")

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, headers=headers, json=data)
                response.raise_for_status()

                # 处理SSE流式响应
                audio_chunks = []
                audio_uri = ""

                async for line in response.aiter_lines():
                    if not line.strip() or not line.startswith('data:'):
                        continue

                    try:
                        # 移除 'data:' 前缀并解析JSON
                        json_str = line.replace('data:', '').strip()
                        if not json_str:
                            continue

                        data_json = json.loads(json_str)

                        # 检查响应码
                        if data_json.get('code') == 0 and data_json.get('data'):
                            # 音频数据块
                            audio_chunk = base64.b64decode(data_json['data'])
                            audio_chunks.append(audio_chunk)
                            print(f"[DEBUG] 收到音频数据块: {len(audio_chunk)} bytes")

                        elif data_json.get('code') == 20000000:
                            # 完成，获取音频URI
                            audio_uri = data_json.get('url', '')
                            print(f"[DEBUG] TTS合成完成，音频URI: {audio_uri}")
                            break

                        elif data_json.get('code') > 0:
                            # 错误
                            raise Exception(f"TTS API错误: {data_json.get('message', '未知错误')}")

                    except json.JSONDecodeError as e:
                        print(f"[DEBUG] JSON解析错误: {e}")
                        continue

                # 合并所有音频数据
                audio_data = b"".join(audio_chunks)
                audio_size = len(audio_data)

                print(f"[DEBUG] TTS合成成功，总音频大小: {audio_size} bytes")

                return {
                    "audio_data": audio_data,
                    "audio_size": audio_size,
                    "format": audio_format,
                    "sample_rate": sample_rate,
                    "speaker": speaker,
                    "method": "tts",
                    "audio_uri": audio_uri
                }

        except Exception as e:
            print(f"[DEBUG] TTS语音合成失败: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"[DEBUG] 降级到演示模式")
            return self._demo_mode(f"TTS API调用失败: {str(e)}")

    def _demo_mode(self, error_reason: str) -> Dict[str, Any]:
        """
        演示模式：返回模拟的音频数据

        使用静音音频数据（有效的 MP3 文件）
        """
        # 返回一个有效的静音 MP3 文件（1秒静音）
        # 这是一个有效的 MP3 文件头，包含静音数据
        demo_audio_data = bytes([
            0xFF, 0xFB, 0x90, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
        ])

        return {
            "audio_data": demo_audio_data,
            "audio_size": len(demo_audio_data),
            "format": "mp3",
            "sample_rate": 24000,
            "speaker": "demo",
            "method": "demo",
            "note": f"当前为演示模式，原因：{error_reason}。请在 .env 文件中配置豆包API Key（DOUBAO_API_KEY）"
        }

    def get_available_speakers(self) -> Dict[str, str]:
        """
        获取可用的音色列表

        Returns:
            音色字典 {name: description}
        """
        return {
            # 通用音色
            "zh_female_xiaohe_uranus_bigtts": "小荷（默认女声，通用）",
            "zh_female_vv_uranus_bigtts": "薇薇（中英文双语女声）",
            "zh_male_m191_uranus_bigtts": "云舟（男声）",
            "zh_male_taocheng_uranus_bigtts": "小天（男声）",

            # 有声书/朗读
            "zh_female_xueayi_saturn_bigtts": "雪姨（儿童有声书）",

            # 视频配音
            "zh_male_dayi_saturn_bigtts": "大义（男声）",
            "zh_female_mizai_saturn_bigtts": "米哉（女声）",
            "zh_female_jitangnv_saturn_bigtts": "鸡汤女（励志女声）",
            "zh_female_meilinvyou_saturn_bigtts": "美女友（魅力女友）",
            "zh_female_santongyongns_saturn_bigtts": "三通女（温柔女声）",
            "zh_male_ruyayichen_saturn_bigtts": "儒雅辰（优雅男声）",

            # 角色扮演
            "saturn_zh_female_keainvsheng_tob": "可爱女生",
            "saturn_zh_female_tiaopigongzhu_tob": "调皮公主",
            "saturn_zh_male_shuanglangshaonian_tob": "爽朗少年",
            "saturn_zh_male_tiancaitongzhuo_tob": "天才同桌",
            "saturn_zh_female_cancan_tob": "聪聪（知性）"
        }


# 创建全局客户端实例
asr_client = DoubaoASRClient()
vision_client = DoubaoVisionClient()
tts_client = DoubaoTTSClient()