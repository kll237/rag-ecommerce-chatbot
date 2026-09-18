"""
百度语音识别API客户端
提供高质量的语音识别服务
"""
import httpx
import base64
import hashlib
import json
from typing import Optional, Dict, Any
from .config import config


class BaiduASRClient:
    """百度语音识别客户端"""

    def __init__(self):
        self.app_id = config.BAIDU_ASR_APP_ID
        self.api_key = config.BAIDU_ASR_API_KEY
        self.secret_key = config.BAIDU_ASR_SECRET_KEY
        self.access_token = None
        self.token_expire_time = 0

    async def _get_access_token(self) -> str:
        """
        获取百度API访问令牌

        Returns:
            access_token字符串
        """
        # 检查token是否过期（有效期2592000秒=30天）
        import time
        current_time = time.time()
        if self.access_token and current_time < self.token_expire_time:
            return self.access_token

        # 获取新的token
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.api_key,
            "client_secret": self.secret_key
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, params=params)
            response.raise_for_status()
            result = response.json()

            if "access_token" not in result:
                raise Exception(f"获取access_token失败: {result}")

            self.access_token = result["access_token"]
            self.token_expire_time = current_time + result.get("expires_in", 2592000) - 3600  # 提前1小时过期

            return self.access_token

    async def recognize(self, audio_data: str, uid: str = "default") -> Dict[str, Any]:
        """
        语音识别（音频转文字）

        使用百度语音识别API进行语音识别

        Args:
            audio_data: base64编码的音频数据
            uid: 用户ID

        Returns:
            包含识别结果的字典
        """
        # 检查配置
        if not self.app_id or self.app_id == "your-baidu-asr-app-id":
            raise Exception("未配置百度语音识别凭证，请在.env中设置BAIDU_ASR_APP_ID、BAIDU_ASR_API_KEY和BAIDU_ASR_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise Exception("未配置百度语音识别API Key和Secret Key")

        try:
            # 获取access_token
            access_token = await self._get_access_token()

            # 将base64音频数据解码为字节数据
            audio_bytes = base64.b64decode(audio_data)
            audio_len = len(audio_bytes)

            # 百度语音识别API端点
            url = f"https://vop.baidu.com/server_api"

            # 构建请求参数
            params = {
                "dev_pid": 1537,  # 1537表示普通话(支持简单的英文识别)
                "token": access_token,
                "cuid": uid,      # 用户唯一标识
            }

            # 构建请求头
            headers = {
                "Content-Type": "audio/wav; rate=16000",
                "Content-Length": str(audio_len)
            }

            # 调用百度语音识别API
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"[DEBUG] 调用百度语音识别API，音频大小: {audio_len} bytes")
                response = await client.post(url, params=params, headers=headers, content=audio_bytes)
                response.raise_for_status()
                result = response.json()
                print(f"[DEBUG] 百度语音识别API响应: {result}")

                # 检查API返回结果
                if result.get("err_no") == 0:
                    # 识别成功
                    result_text = result.get("result", [""])[0] if result.get("result") else ""
                    print(f"[DEBUG] 识别成功: {result_text}")

                    return {
                        "text": result_text.strip(),
                        "duration": audio_len / 32000,  # 估算时长（假设16kHz采样率）
                        "model": "baidu-asr",
                        "method": "baidu",
                        "confidence": result.get("confidence", 0)  # 置信度
                    }
                else:
                    # 识别失败
                    error_msg = result.get("err_msg", "未知错误")
                    error_code = result.get("err_no")
                    print(f"[DEBUG] 百度语音识别失败: [{error_code}] {error_msg}")
                    raise Exception(f"百度语音识别失败 [{error_code}]: {error_msg}")

        except httpx.HTTPStatusError as e:
            # HTTP错误
            error_text = e.response.text if e.response else str(e)
            print(f"[DEBUG] 百度语音识别HTTP错误: {e.response.status_code} - {error_text}")
            raise Exception(f"百度语音识别HTTP错误: {e.response.status_code} - {error_text}")

        except Exception as e:
            # 其他异常
            print(f"[DEBUG] 百度语音识别异常: {type(e).__name__}: {str(e)}")
            raise Exception(f"百度语音识别异常: {str(e)}")

    def get_setup_guide(self) -> str:
        """
        获取百度语音识别API配置指南

        Returns:
            配置指南文本
        """
        return """
# 百度语音识别API配置指南

## 1. 开通百度语音识别服务

1. 访问百度智能云：https://cloud.baidu.com/
2. 注册/登录账号
3. 进入控制台，搜索"语音识别"
4. 点击"立即使用"或"免费试用"（新用户有免费额度）

## 2. 创建应用

1. 在语音识别控制台，点击"创建应用"
2. 填写应用名称（例如：电商客服系统）
3. 选择应用类型（选择"语音技术"）
4. 提交后等待审核（通常即时通过）

## 3. 获取API凭证

创建应用成功后，会显示以下信息：
- AppID：应用ID
- API Key：API密钥
- Secret Key：密钥

## 4. 配置环境变量

在 `backend/.env` 文件中添加以下配置：

```bash
# 百度语音识别配置
BAIDU_ASR_APP_ID=你的AppID
BAIDU_ASR_API_KEY=你的API_Key
BAIDU_ASR_SECRET_KEY=你的Secret_Key
"""