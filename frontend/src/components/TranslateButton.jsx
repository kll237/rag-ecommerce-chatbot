import React, { useState, useRef, useEffect } from 'react';

function TranslateButton({ content, currentLanguage, onTranslated }) {
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  // 点击外部关闭下拉菜单
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  // 调用后端翻译API
  const translateText = async (targetLanguage) => {
    setLoading(true);
    setIsOpen(false);

    try {
      const response = await fetch('http://localhost:8000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: content,
          target_language: targetLanguage
        })
      });

      if (!response.ok) {
        throw new Error(`翻译请求失败: ${response.status}`);
      }

      const data = await response.json();
      // 将翻译结果传递给父组件
      if (onTranslated) {
        onTranslated(data.translated_text, targetLanguage);
      }
    } catch (error) {
      console.error('翻译失败:', error);
      alert('翻译失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <button className="translate-button loading" disabled>
        翻译中...
      </button>
    );
  }

  return (
    <div className="translate-container" ref={dropdownRef}>
      <button
        className="translate-button"
        onClick={() => setIsOpen(!isOpen)}
        title="翻译"
      >
        🌐 翻译
      </button>

      {isOpen && (
        <div className="translate-dropdown">
          <div className="translate-header">翻译到:</div>
          <div className="translate-options">
            <button onClick={() => translateText('en')}>English</button>
            <button onClick={() => translateText('ja')}>日本語</button>
            <button onClick={() => translateText('ko')}>한국어</button>
            <button onClick={() => translateText('fr')}>Français</button>
            <button onClick={() => translateText('es')}>Español</button>
            <button onClick={() => translateText('de')}>Deutsch</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default TranslateButton;