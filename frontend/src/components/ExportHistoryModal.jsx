import { useState } from 'react';
import { X, Download, FileText, FileJson } from 'lucide-react';

const ExportHistoryModal = ({ isOpen, onClose, session_id, API_BASE_URL }) => {
  const [format, setFormat] = useState('txt');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleExport = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`${API_BASE_URL}/chat/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: session_id,
          format: format
        }),
      });

      if (!response.ok) {
        throw new Error('导出失败');
      }

      // 获取文件名
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition && contentDisposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch ? filenameMatch[1] : `chat_history.${format}`;

      // 下载文件
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);

      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md">
        {/* 标题栏 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Download className="w-6 h-6 text-indigo-600" />
            <h2 className="text-2xl font-bold text-gray-800">导出对话历史</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* 内容区 */}
        <div className="p-6 space-y-6">
          {/* 格式选择 */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              选择导出格式
            </label>
            <div className="grid grid-cols-2 gap-4">
              {/* TXT 格式 */}
              <button
                onClick={() => setFormat('txt')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  format === 'txt'
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-800'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileText className="w-8 h-8 mx-auto mb-2" />
                <div className="font-medium">TXT 文本</div>
                <div className="text-sm text-gray-500 mt-1">纯文本格式</div>
              </button>

              {/* JSON 格式 */}
              <button
                onClick={() => setFormat('json')}
                className={`p-4 rounded-xl border-2 transition-all ${
                  format === 'json'
                    ? 'border-indigo-600 bg-indigo-50 text-indigo-800'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <FileJson className="w-8 h-8 mx-auto mb-2" />
                <div className="font-medium">JSON 数据</div>
                <div className="text-sm text-gray-500 mt-1">结构化数据</div>
              </button>
            </div>
          </div>

          {/* 会话信息 */}
          <div className="bg-gray-50 p-4 rounded-xl">
            <div className="text-sm text-gray-600">
              <div className="font-medium text-gray-800 mb-1">会话信息</div>
              <div className="font-mono text-xs break-all">
                ID: {session_id}
              </div>
            </div>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="text-red-500 text-sm bg-red-50 p-3 rounded-lg">
              {error}
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="border-t border-gray-200 p-6">
          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={loading}
              className="flex-1 px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors font-medium disabled:opacity-50"
            >
              取消
            </button>
            <button
              onClick={handleExport}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  导出中...
                </>
              ) : (
                <>
                  <Download className="w-5 h-5" />
                  开始导出
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExportHistoryModal;