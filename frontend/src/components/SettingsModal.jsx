import React, { useState, useEffect } from 'react';
import { getSpeakers } from '../utils/tts';

function SettingsModal({ isOpen, onClose, settings, onSave }) {
  const [localSettings, setLocalSettings] = useState(settings);
  const [speakers, setSpeakers] = useState([]);

  useEffect(() => {
    if (isOpen) {
      setLocalSettings(settings);
      // 加载音色列表
      loadSpeakers();
    }
  }, [isOpen, settings]);

  const loadSpeakers = async () => {
    try {
      const speakerList = await getSpeakers();
      setSpeakers(speakerList);
    } catch (error) {
      console.error('加载音色列表失败:', error);
    }
  };

  const handleThemeChange = (theme) => {
    setLocalSettings({ ...localSettings, theme });
  };

  const handleLanguageChange = (language) => {
    setLocalSettings({ ...localSettings, language });
  };

  const handleSave = () => {
    onSave(localSettings);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content settings-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>设置</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* 主题设置 */}
          <div className="setting-group">
            <h3>主题</h3>
            <div className="setting-options">
              <button
                className={`theme-button ${localSettings.theme === 'light' ? 'active' : ''}`}
                onClick={() => handleThemeChange('light')}
              >
                ☀️ 浅色
              </button>
              <button
                className={`theme-button ${localSettings.theme === 'dark' ? 'active' : ''}`}
                onClick={() => handleThemeChange('dark')}
              >
                🌙 深色
              </button>
            </div>
          </div>

          {/* 语言设置 */}
          <div className="setting-group">
            <h3>语言</h3>
            <div className="setting-options">
              <button
                className={`language-button ${localSettings.language === 'zh' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('zh')}
              >
                中文
              </button>
              <button
                className={`language-button ${localSettings.language === 'en' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('en')}
              >
                English
              </button>
              <button
                className={`language-button ${localSettings.language === 'ja' ? 'active' : ''}`}
                onClick={() => handleLanguageChange('ja')}
              >
                日本語
              </button>
            </div>
          </div>

          {/* 其他设置 */}
          <div className="setting-group">
            <h3>其他</h3>
            <label className="setting-checkbox">
              <input
                type="checkbox"
                checked={localSettings.soundEnabled}
                onChange={(e) => setLocalSettings({ ...localSettings, soundEnabled: e.target.checked })}
              />
              <span>开启提示音</span>
            </label>
          </div>

          {/* 语音合成设置 */}
          <div className="setting-group">
            <h3>语音合成（TTS）</h3>
            <label className="setting-checkbox">
              <input
                type="checkbox"
                checked={localSettings.ttsEnabled || false}
                onChange={(e) => setLocalSettings({ ...localSettings, ttsEnabled: e.target.checked })}
              />
              <span>开启语音播放</span>
            </label>

            {localSettings.ttsEnabled && (
              <>
                <div className="setting-subsection">
                  <label>音色选择：</label>
                  <select
                    className="setting-select"
                    value={localSettings.ttsSpeaker || 'zh_female_xiaohe_uranus_bigtts'}
                    onChange={(e) => setLocalSettings({ ...localSettings, ttsSpeaker: e.target.value })}
                  >
                    {speakers.map((speaker) => (
                      <option key={speaker.id} value={speaker.id}>
                        {speaker.name} ({speaker.category})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="setting-subsection">
                  <label>音频格式：</label>
                  <select
                    className="setting-select"
                    value={localSettings.ttsAudioFormat || 'mp3'}
                    onChange={(e) => setLocalSettings({ ...localSettings, ttsAudioFormat: e.target.value })}
                  >
                    <option value="mp3">MP3</option>
                    <option value="pcm">PCM</option>
                    <option value="ogg_opus">OGG Opus</option>
                  </select>
                </div>

                <div className="setting-subsection">
                  <label>采样率：</label>
                  <select
                    className="setting-select"
                    value={localSettings.ttsSampleRate || 24000}
                    onChange={(e) => setLocalSettings({ ...localSettings, ttsSampleRate: parseInt(e.target.value) })}
                  >
                    <option value="8000">8000 Hz</option>
                    <option value="16000">16000 Hz</option>
                    <option value="22050">22050 Hz</option>
                    <option value="24000">24000 Hz</option>
                    <option value="32000">32000 Hz</option>
                    <option value="44100">44100 Hz</option>
                    <option value="48000">48000 Hz</option>
                  </select>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button className="cancel-button" onClick={onClose}>取消</button>
          <button className="save-button" onClick={handleSave}>保存</button>
        </div>
      </div>
    </div>
  );
}

export default SettingsModal;