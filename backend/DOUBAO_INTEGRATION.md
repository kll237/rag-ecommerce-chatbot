# 豆包API集成说明

## 📋 概述

本项目已成功集成豆包API，支持以下功能：

1. **语音识别（ASR）** - 将音频转换为文字
2. **图片识别（Vision）** - 使用多模态大模型识别商品

## ✅ 已完成的修改

### 1. backend/app/main.py

#### 语音识别端点（第320-360行）
```python
@app.post("/voice/recognize", response_model=VoiceRecognizeResponse)
async def recognize_voice(request: VoiceRecognizeRequest):
    """
    使用豆包语音识别服务将音频转换为文字
    支持格式：MP3, WAV, PCM, OGG
    """
    sdk_config = Config()
    asr_client = ASRClient(sdk_config)

    result = asr_client.recognize({
        'uid': str(uuid.uuid4()),
        'base64Data': request.audio_data
    })

    return VoiceRecognizeResponse(
        text=result.text,
        duration=result.duration
    )