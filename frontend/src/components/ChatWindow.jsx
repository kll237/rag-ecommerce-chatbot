import React, { useState, useEffect, useRef } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import SettingsModal from './SettingsModal';
import ExportHistoryModal from './ExportHistoryModal';
import { ShoppingBag, Heart, Download, Settings } from 'lucide-react';
import { sendMessage } from '../api/api';

// 快捷回复问题
const QUICK_REPLIES = [
  '怎么查询订单状态',
  '什么时候发货',
  '支持哪些支付方式',
  '可以退货吗',
  '你们有什么产品',
  '包邮吗'
];

function ChatWindow({ session, onUpdateSession, onNavigateToCart, onNavigateToWishlist }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [exportOpen, setExportOpen] = useState(false);
  const [settings, setSettings] = useState({
    theme: 'light',
    language: 'zh',
    soundEnabled: true,
    ttsEnabled: false,
    ttsSpeaker: 'zh_female_xiaohe_uranus_bigtts',
    ttsAudioFormat: 'mp3',
    ttsSampleRate: 24000
  });
  const messagesEndRef = useRef(null);

  // 加载保存的设置
  useEffect(() => {
    const savedSettings = localStorage.getItem('chatSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
      applySettings(JSON.parse(savedSettings));
    }
  }, []);

  useEffect(() => {
    if (session && session.messages) {
      setMessages(session.messages);
    } else {
      setMessages([]);
    }
  }, [session]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const applySettings = (newSettings) => {
    // 应用主题
    if (newSettings.theme === 'dark') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  };

  const handleSettingsSave = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('chatSettings', JSON.stringify(newSettings));
    applySettings(newSettings);
  };

  const handleSendMessage = async (message, imageData = null) => {
    if ((!message.trim() && !imageData) || loading) return;

    // 添加用户消息
    const userMessage = {
      role: 'user',
      content: message,
      image: imageData,  // 添加图片数据
      timestamp: new Date().toISOString()
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);

    setLoading(true);

    try {
      // 如果有图片，先识别图片
      let imageRecognitionResult = null;
      if (imageData) {
        try {
          // 将图片URL转换为base64（如果是URL）
          let imageBase64 = imageData;
          if (imageData.startsWith('data:image/')) {
            // 已经是base64格式，提取纯数据部分
            imageBase64 = imageData.split(',')[1];
          }

          const imageResponse = await fetch('http://localhost:8000/image/recognize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              image_data: imageBase64,
              question: '请识别这张图片中的商品，提供商品名称、类别、价格范围和特征'
            }),
          });

          if (imageResponse.ok) {
            imageRecognitionResult = await imageResponse.json();

            // 添加图片识别结果作为助手消息
            const recognitionMessage = {
              role: 'assistant',
              content: formatImageRecognitionResult(imageRecognitionResult),
              image: imageData,
              isRecognition: true,
              timestamp: new Date().toISOString()
            };
            updatedMessages.push(recognitionMessage);
            setMessages([...updatedMessages]);
          }
        } catch (imageError) {
          console.error('图片识别失败:', imageError);
        }
      }

      // 构建查询文本（包含图片识别结果）
      let queryText = message;
      if (imageRecognitionResult) {
        queryText = `${message || ''}（图片识别：${imageRecognitionResult.product_name || '未知商品'}）`;
      }

      // 调用API
      const response = await sendMessage({
        query: queryText || '请介绍这个商品',
        session_id: session?.id,
        top_k: 5
      });

      // 添加助手消息
      const assistantMessage = {
        id: response.message_id,
        role: 'assistant',
        content: response.answer,
        intent: response.intent,
        confidence: response.confidence,
        retrieved_docs: response.retrieved_docs,
        suggested_products: response.suggested_products,
        timestamp: new Date().toISOString()
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      // 更新会话
      if (onUpdateSession && session) {
        onUpdateSession({
          ...session,
          messages: finalMessages
        });
      }
    } catch (error) {
      console.error('发送消息失败:', error);

      // 添加错误消息
      const errorMessage = {
        role: 'assistant',
        content: '抱歉，发生了错误，请稍后重试。',
        isError: true,
        timestamp: new Date().toISOString()
      };

      setMessages([...updatedMessages, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatImageRecognitionResult = (result) => {
    let text = '';

    if (result.product_name) {
      text += `📦 **商品名称**: ${result.product_name}\n\n`;
    }

    if (result.category) {
      text += `🏷️ **类别**: ${result.category}\n\n`;
    }

    if (result.description) {
      text += `📝 **描述**: ${result.description}\n\n`;
    }

    if (result.features && result.features.length > 0) {
      text += `✨ **特征**:\n`;
      result.features.forEach(feature => {
        text += `• ${feature}\n`;
      });
      text += '\n';
    }

    if (result.suggested_price) {
      text += `💰 **价格范围**: ${result.suggested_price}\n\n`;
    }

    text += '💡 正在为您查找更多相关信息...';

    return text;
  };

  if (!session) {
    return (
      <div className="chat-window empty">
        <div className="empty-state">
          <div className="empty-icon">💬</div>
          <h2>开始新的对话</h2>
          <p>点击上方的"+ 新对话"按钮开始聊天</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <div className="header-left">
          <h3>{session.title || '对话'}</h3>
          <div className="chat-meta">
            <span className="message-count">{messages.length} 条消息</span>
          </div>
        </div>

        {/* 工具栏 */}
        <div className="header-right">
          <button
            onClick={onNavigateToCart}
            className="toolbar-button"
            title="购物车"
          >
            <ShoppingBag className="w-5 h-5" />
          </button>
          <button
            onClick={onNavigateToWishlist}
            className="toolbar-button"
            title="我的收藏"
          >
            <Heart className="w-5 h-5" />
          </button>
          <button
            onClick={() => setExportOpen(true)}
            className="toolbar-button"
            title="导出对话历史"
          >
            <Download className="w-5 h-5" />
          </button>
          <button
            onClick={() => setSettingsOpen(true)}
            className="toolbar-button"
            title="设置"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      <div className="chat-messages">
        <MessageList
          messages={messages}
          currentLanguage={settings.language}
          ttsSettings={{
            enabled: settings.ttsEnabled,
            speaker: settings.ttsSpeaker,
            audioFormat: settings.ttsAudioFormat,
            sampleRate: settings.ttsSampleRate
          }}
        />

        {/* 快捷回复 - 仅在无消息时显示 */}
        {messages.length === 0 && !loading && (
          <div className="quick-replies">
            <div className="quick-replies-title">快速开始</div>
            <div className="quick-replies-buttons">
              {QUICK_REPLIES.map((reply, index) => (
                <button
                  key={index}
                  className="quick-reply-button"
                  onClick={() => handleSendMessage(reply)}
                  disabled={loading}
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="message assistant loading">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <MessageInput
        onSendMessage={handleSendMessage}
        disabled={loading}
        onSettingsClick={() => setSettingsOpen(true)}
      />

      <SettingsModal
        isOpen={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        settings={settings}
        onSave={handleSettingsSave}
      />

      {/* 导出历史模态框 */}
      <ExportHistoryModal
        isOpen={exportOpen}
        onClose={() => setExportOpen(false)}
        session_id={session?.id}
        API_BASE_URL="http://localhost:8000"
      />
    </div>
  );
}

export default ChatWindow;
