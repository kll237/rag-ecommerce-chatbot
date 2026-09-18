import React, { useState, useRef, useEffect } from 'react';

function MessageInput({ onSendMessage, disabled, onSettingsClick }) {
  const [message, setMessage] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [showImagePreview, setShowImagePreview] = useState(false);
  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if ((message.trim() || selectedImage) && !disabled) {
      onSendMessage(message.trim(), selectedImage);
      setMessage('');
      setSelectedImage(null);
      setShowImagePreview(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // 语音录制功能
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioBase64 = await blobToBase64(audioBlob);

        // 调用后端语音识别API
        await recognizeVoice(audioBase64);

        // 停止所有音频轨道
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('无法访问麦克风:', error);
      alert('无法访问麦克风，请检查权限设置');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleVoiceButtonClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  const blobToBase64 = (blob) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(blob);
      reader.onloadend = () => {
        const base64data = reader.result.split(',')[1];
        resolve(base64data);
      };
      reader.onerror = reject;
    });
  };

  const recognizeVoice = async (audioBase64) => {
    try {
      const response = await fetch('http://localhost:8000/voice/recognize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          audio_data: audioBase64,
          audio_format: 'webm'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessage(data.text);
      } else {
        console.error('语音识别失败:', response.statusText);
        alert('语音识别失败，请重试');
      }
    } catch (error) {
      console.error('语音识别错误:', error);
      alert('语音识别失败，请重试');
    }
  };

  // 图片上传功能
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      // 检查文件大小（限制5MB）
      if (file.size > 5 * 1024 * 1024) {
        alert('图片大小不能超过5MB');
        return;
      }

      // 检查文件类型
      if (!file.type.startsWith('image/')) {
        alert('请上传图片文件');
        return;
      }

      const reader = new FileReader();
      reader.onload = (event) => {
        setSelectedImage(event.target.result);
        setShowImagePreview(true);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setShowImagePreview(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <form className="message-input" onSubmit={handleSubmit}>
      {showImagePreview && selectedImage && (
        <div className="image-preview">
          <img src={selectedImage} alt="预览" />
          <button type="button" className="remove-image-button" onClick={handleRemoveImage}>
            ✕
          </button>
        </div>
      )}

      <div className="input-border-container">
        {isRecording && (
          <div className="recording-indicator">
            🎙️ 正在录音... (点击停止)
          </div>
        )}

        <div className="input-container">
          <div className="input-actions-left">
            {/* 图片上传按钮 */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ display: 'none' }}
            />
            <button
              type="button"
              className="icon-button"
              onClick={() => fileInputRef.current?.click()}
              title="上传图片"
              disabled={disabled}
            >
              📷
            </button>

            {/* 语音录制按钮 */}
            <button
              type="button"
              className={`icon-button ${isRecording ? 'recording' : ''}`}
              onClick={handleVoiceButtonClick}
              title={isRecording ? '停止录音' : '开始录音'}
              disabled={disabled}
            >
              {isRecording ? '🛑' : '🎤'}
            </button>
          </div>

          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="输入您的问题或上传图片... (Enter 发送，Shift+Enter 换行)"
            disabled={disabled}
            rows={1}
          />

          <div className="input-actions-right">
            <button
              type="button"
              className="settings-button"
              onClick={onSettingsClick}
              title="设置"
            >
              ⚙️
            </button>
            <button
              type="submit"
              className="send-button"
              disabled={disabled || (!message.trim() && !selectedImage)}
            >
              {disabled ? '发送中...' : '发送'}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}

export default MessageInput;