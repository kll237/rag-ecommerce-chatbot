import React, { useState } from 'react';
import ProductCard from './ProductCard';
import TranslateButton from './TranslateButton';
import { textToSpeech, playBase64Audio } from '../utils/tts';

function MessageList({ messages, currentLanguage, ttsSettings }) {
  if (!messages || messages.length === 0) {
    return (
      <div className="message-list empty">
        <p>开始对话吧！我可以帮助您解答关于产品、订单、支付等问题。</p>
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((message, index) => (
        <Message
          key={index}
          message={message}
          currentLanguage={currentLanguage}
          ttsSettings={ttsSettings}
        />
      ))}
    </div>
  );
}

function Message({ message, currentLanguage, ttsSettings }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState(message.feedback || null);
  const [translatedText, setTranslatedText] = useState('');
  const [targetLanguage, setTargetLanguage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [showFeedbackThanks, setShowFeedbackThanks] = useState(false);
  const [feedbackType, setFeedbackType] = useState(null);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  const handleFeedback = async (rating) => {
    try {
      const response = await fetch('http://localhost:8000/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: message.id,
          rating: rating,
          is_helpful: rating > 3
        })
      });

      if (response.ok) {
        setFeedback(rating);
        setFeedbackType(rating);
        setShowFeedbackThanks(true);

        // 3秒后自动隐藏感谢消息
        setTimeout(() => {
          setShowFeedbackThanks(false);
        }, 3000);
      }
    } catch (err) {
      console.error('提交反馈失败:', err);
    }
  };

  const handleTranslated = (text, lang) => {
    setTranslatedText(text);
    setTargetLanguage(lang);
  };

  const handlePlayAudio = async () => {
    if (isPlaying) return;

    if (!ttsSettings?.enabled) {
      alert('请在设置中开启语音播放功能');
      return;
    }

    try {
      setIsPlaying(true);

      // 调用 TTS API
      const result = await textToSpeech(message.content, {
        speaker: ttsSettings.speaker || 'zh_female_xiaohe_uranus_bigtts',
        audioFormat: ttsSettings.audioFormat || 'mp3'
      });

      // 检查音频数据是否为空或是否为演示模式
      if (result.method === 'demo' || !result.audio_data || result.audio_size === 0) {
        // 演示模式提示
        const note = result.note || '未配置豆包API Key';
        alert(`⚠️ 语音合成提示\n\n${note}\n\n如需使用真实语音功能，请在后端 .env 文件中配置 DOUBAO_API_KEY`);
        return;
      }

      // 播放音频
      await playBase64Audio(result.audio_data);
    } catch (error) {
      console.error('播放语音失败:', error);
      alert('⚠️ 语音播放失败\n\n请检查：\n1. 网络连接是否正常\n2. 后端服务是否运行\n3. 是否已配置豆包API Key');
    } finally {
      setIsPlaying(false);
    }
  };

  // 重置翻译状态（切换消息时）
  React.useEffect(() => {
    setTranslatedText('');
    setTargetLanguage('');
  }, [message.content]);

  return (
    <div className={`message ${isUser ? 'user' : 'assistant'} ${message.isError ? 'error' : ''}`}>
      <div className="message-avatar">
        {isUser ? '👤' : '🤖'}
      </div>
      <div className="message-content">
        {/* 显示图片（如果有） */}
        {message.image && (
          <div className="message-image">
            <img src={message.image} alt="上传的图片" />
            {message.isRecognition && (
              <div className="recognition-badge">✨ 图片识别</div>
            )}
          </div>
        )}

        <div className="message-text">
          {message.content}
          {!isUser && (
            <>
              <button
                className="copy-button"
                onClick={handleCopy}
                title="复制消息"
              >
                {copied ? '✓ 已复制' : '📋'}
              </button>
              <TranslateButton
                content={message.content}
                currentLanguage={currentLanguage}
                onTranslated={handleTranslated}
              />
              <button
                className={`tts-button ${isPlaying ? 'playing' : ''}`}
                onClick={handlePlayAudio}
                disabled={isPlaying}
                title="播放语音"
              >
                {isPlaying ? '🔊 播放中...' : '🔊'}
              </button>
            </>
          )}
        </div>

        {translatedText && (
          <div style={{ marginTop: '0.5rem', padding: '0.75rem', background: 'rgba(79, 70, 229, 0.1)', borderRadius: '0.5rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#666', marginBottom: '0.25rem' }}>
              翻译结果 ({targetLanguage === 'en' ? 'English' :
                         targetLanguage === 'ja' ? '日本語' :
                         targetLanguage === 'ko' ? '한국어' :
                         targetLanguage === 'fr' ? 'Français' :
                         targetLanguage === 'es' ? 'Español' :
                         targetLanguage === 'de' ? 'Deutsch' : targetLanguage}):
            </div>
            <div style={{ lineHeight: '1.6' }}>{translatedText}</div>
          </div>
        )}

        {message.intent && (
          <div className="message-intent">
            <span className="intent-label">意图:</span>
            <span className="intent-value">{message.intent}</span>
            {message.confidence && (
              <span className="intent-confidence">
                ({(message.confidence * 100).toFixed(0)}%)
              </span>
            )}
          </div>
        )}

        {!isUser && !feedback && (
          <div className="feedback-buttons">
            <span className="feedback-label">这条回答有帮助吗？</span>
            <button
              className="feedback-button"
              onClick={() => handleFeedback(5)}
              title="非常有帮助"
            >
              👍
            </button>
            <button
              className="feedback-button"
              onClick={() => handleFeedback(3)}
              title="一般"
            >
              😐
            </button>
            <button
              className="feedback-button"
              onClick={() => handleFeedback(1)}
              title="没有帮助"
            >
              👎
            </button>
          </div>
        )}

        {/* 反馈感谢消息 */}
        {showFeedbackThanks && !isUser && (
          <div className="feedback-thanks">
            {feedbackType === 5 && '感谢您的反馈！我们会继续努力为您提供更好的服务！'}
            {feedbackType === 3 && '感谢您的反馈，我们会持续改进！'}
            {feedbackType === 1 && '感谢您的反馈，我们会认真改进不足之处！'}
          </div>
        )}

        {/* 推荐商品区域 - 关键优化：移除图标、背景色和边框 */}
        {message.suggested_products && message.suggested_products.length > 0 && (
          <div className="suggested-products">
            <div className="suggested-products-title">
              推荐商品 ({message.suggested_products.length})
            </div>
            <div className="suggested-products-grid">
              {message.suggested_products.map(product => (
                <ProductCard
                  key={product.id}
                  product={product}
                  session_id={message.session_id}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageList;