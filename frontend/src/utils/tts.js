/**
 * 语音合成（TTS）工具函数
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * 获取可用音色列表
 */
export async function getSpeakers() {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/tts/speakers`);
    if (!response.ok) {
      throw new Error('获取音色列表失败');
    }
    const data = await response.json();
    return data.speakers || [];
  } catch (error) {
    console.error('获取音色列表失败:', error);
    return [];
  }
}

/**
 * 文本转语音（返回 base64 音频数据）
 */
export async function textToSpeech(text, options = {}) {
  const {
    speaker = 'zh_female_xiaohe_uranus_bigtts',
    audioFormat = 'mp3',
    sampleRate = 24000,
    speechRate = 0,
    loudnessRate = 0
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/chat/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        speaker,
        audio_format: audioFormat,
        sample_rate: sampleRate,
        speech_rate: speechRate,
        loudness_rate: loudnessRate
      })
    });

    if (!response.ok) {
      throw new Error('语音合成失败');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('语音合成失败:', error);
    throw error;
  }
}

/**
 * 文本转语音（流式返回，可直接播放）
 */
export async function textToSpeechStream(text, options = {}) {
  const {
    speaker = 'zh_female_xiaohe_uranus_bigtts',
    audioFormat = 'mp3'
  } = options;

  try {
    const response = await fetch(`${API_BASE_URL}/chat/tts/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        speaker,
        audio_format: audioFormat
      })
    });

    if (!response.ok) {
      throw new Error('语音合成失败');
    }

    return response.blob();
  } catch (error) {
    console.error('语音合成失败:', error);
    throw error;
  }
}

/**
 * 播放 base64 音频
 */
export function playBase64Audio(base64Data) {
  return new Promise((resolve, reject) => {
    try {
      const audio = new Audio(`data:audio/mpeg;base64,${base64Data}`);

      audio.onended = () => {
        resolve();
      };

      audio.onerror = (error) => {
        reject(error);
      };

      audio.play().catch(reject);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 播放 Blob 音频
 */
export function playBlobAudio(blob) {
  return new Promise((resolve, reject) => {
    try {
      const audioUrl = URL.createObjectURL(blob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        resolve();
      };

      audio.onerror = (error) => {
        URL.revokeObjectURL(audioUrl);
        reject(error);
      };

      audio.play().catch(reject);
    } catch (error) {
      reject(error);
    }
  });
}

/**
 * 停止所有正在播放的音频
 */
export function stopAllAudio() {
  const audios = document.querySelectorAll('audio');
  audios.forEach(audio => {
    audio.pause();
    audio.currentTime = 0;
  });
}