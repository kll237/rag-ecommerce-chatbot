# 语音识别功能说明

## 当前状态

语音识别功能已集成到系统中，使用 OpenAI Whisper 开源模型进行本地语音识别。

## 功能描述

- **端点**: `/voice/recognize`
- **功能**: 将用户录制的语音转换为文字
- **支持格式**: MP3, WAV, PCM, OGG, WebM
- **前端集成**: 已在 MessageInput 组件中实现录音按钮
- **识别模型**: Whisper (base)，支持中英文识别

## 安装依赖

### 1. 安装 Python 包

在 PyCharm 的终端中执行：

```bash
cd backend
pip install openai-whisper==20231117 ffmpeg-python==0.2.0