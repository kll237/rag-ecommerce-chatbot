import React, { useState } from 'react';
import { Trash2, CheckSquare, Square, MessageSquare, Search, Columns, X } from 'lucide-react';

function ChatHistory({ sessions, currentSession, onSelectSession, onDeleteSessions, allSessions }) {
  const [selectedSessionIds, setSelectedSessionIds] = useState(new Set());
  const [isSelectionMode, setIsSelectionMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCompareModal, setShowCompareModal] = useState(false);

  const toggleSelection = (sessionId) => {
    if (!sessionId) {
      console.warn('Invalid sessionId:', sessionId);
      return;
    }
    const newSelection = new Set(selectedSessionIds);
    if (newSelection.has(sessionId)) {
      newSelection.delete(sessionId);
    } else {
      newSelection.add(sessionId);
    }
    setSelectedSessionIds(newSelection);
  };

  const toggleSelectAll = () => {
    if (selectedSessionIds.size === sessions.length) {
      setSelectedSessionIds(new Set());
    } else {
      const validIds = sessions
        .map(s => s.dbId)
        .filter(id => id !== null && id !== undefined);
      console.log('Valid session IDs for select all:', validIds);
      setSelectedSessionIds(new Set(validIds));
    }
  };

  const handleDelete = async () => {
    const validIds = Array.from(selectedSessionIds).filter(id => id !== null && id !== undefined);
    console.log('Attempting to delete session IDs:', validIds);

    if (validIds.length === 0) {
      alert('请先选择要删除的会话');
      return;
    }

    if (!window.confirm(`确定要删除选中的 ${validIds.length} 个会话吗？`)) {
      return;
    }

    try {
      await onDeleteSessions(validIds);
      setSelectedSessionIds(new Set());
      setIsSelectionMode(false);
    } catch (error) {
      alert('删除失败，请重试');
    }
  };

  const handleSessionClick = (session) => {
    if (isSelectionMode) {
      // 选择模式下点击切换选中状态
      toggleSelection(session.dbId);
    } else {
      // 正常模式下点击切换会话
      onSelectSession(session);
    }
  };

  // 根据搜索查询过滤会话
  const filteredSessions = sessions.filter(session => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    // 搜索会话标题
    const titleMatch = session.title?.toLowerCase().includes(query);
    // 如果会话已加载消息，搜索消息内容
    const messageMatch = session.messages?.some(msg =>
      msg.content?.toLowerCase().includes(query)
    );
    return titleMatch || messageMatch;
  });

  return (
    <div className="chat-history">
      <div className="history-header">
        <div className="history-header-content">
          <div className="history-header-left">
            <h3>历史会话</h3>
            <span className="session-count">{filteredSessions.length}</span>
          </div>
          <button
            className={`selection-toggle-btn ${isSelectionMode ? 'selection-mode-active' : ''}`}
            onClick={() => setIsSelectionMode(!isSelectionMode)}
          >
            <MessageSquare className="w-3 h-3" />
            <span>{isSelectionMode ? '退出选择' : '选择'}</span>
          </button>
        </div>

        {/* 搜索框 - 美化版本 */}
        <div className="search-box-wrapper mt-3">
          <div className="search-box-container relative">
            <div className="search-icon-wrapper">
              <Search className="search-icon" />
            </div>
            <input
              type="text"
              placeholder="搜索会话或消息内容..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="clear-search-btn"
              >
                <X className="w-3 h-3" />
              </button>
            )}
            {searchQuery && (
              <div className="search-results-badge">
                {filteredSessions.length} 个结果
              </div>
            )}
          </div>
        </div>

        {/* 选择模式下的操作栏 - 紧凑版本 */}
        {isSelectionMode && (
          <div className="selection-toolbar mt-2">
            <div className="selection-toolbar-content">
              <button
                className="select-all-btn"
                onClick={toggleSelectAll}
              >
                {selectedSessionIds.size === sessions.length ? (
                  <CheckSquare className="w-3 h-3" />
                ) : (
                  <Square className="w-3 h-3" />
                )}
                <span>{selectedSessionIds.size === sessions.length ? '取消全选' : '全选'}</span>
              </button>

              <div className="action-buttons-group">
                <button
                  className="compare-btn"
                  onClick={() => setShowCompareModal(true)}
                  disabled={selectedSessionIds.size === 0 || selectedSessionIds.size > 4}
                  title="对比选中的会话"
                >
                  <Columns className="w-3 h-3" />
                  <span>对比</span>
                  {selectedSessionIds.size > 0 && (
                    <span className="action-badge">{selectedSessionIds.size}</span>
                  )}
                </button>
                <button
                  className="delete-btn"
                  onClick={handleDelete}
                  disabled={selectedSessionIds.size === 0}
                  title="删除选中的会话"
                >
                  <Trash2 className="w-3 h-3" />
                  <span>删除</span>
                  {selectedSessionIds.size > 0 && (
                    <span className="action-badge">{selectedSessionIds.size}</span>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="history-list">
        {filteredSessions.length === 0 ? (
          <div className="empty-history">
            <MessageSquare className="w-12 h-12 text-gray-300 mb-2" />
            <p>{searchQuery ? '未找到匹配的会话' : '暂无历史会话'}</p>
          </div>
        ) : (
          filteredSessions.map(session => {
            const isSelected = selectedSessionIds.has(session.dbId);
            if (session.dbId === null || session.dbId === undefined) {
              console.warn('Session missing dbId:', session);
            }
            return (
              <div
                key={session.id}
                className={`history-item ${currentSession?.id === session.id ? 'active' : ''} ${
                  isSelectionMode ? 'selection-mode' : ''
                }`}
                onClick={() => handleSessionClick(session)}
              >
                {isSelectionMode && (
                  <div className="history-item-checkbox">
                    {isSelected ? (
                      <CheckSquare className="w-4 h-4 text-blue-600" />
                    ) : (
                      <Square className="w-4 h-4 text-gray-400" />
                    )}
                  </div>
                )}
                <div className="history-item-content">
                  <div className="history-item-title">
                    {session.title}
                  </div>
                  <div className="history-item-meta">
                    {session.createdAt ? new Date(session.createdAt).toLocaleString('zh-CN', {
                      year: 'numeric',
                      month: '2-digit',
                      day: '2-digit',
                      hour: '2-digit',
                      minute: '2-digit'
                    }) : '未知时间'}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 会话对比弹窗 - 美化版本 */}
      {showCompareModal && (
        <div className="compare-modal-overlay">
          <div className="compare-modal-content">
            <div className="compare-modal-header">
              <div className="header-left">
                <div className="header-icon-wrapper">
                  <Columns className="w-5 h-5" />
                </div>
                <div>
                  <h3>会话对比</h3>
                  <p>已选择 {selectedSessionIds.size} 个会话</p>
                </div>
              </div>
              <button
                onClick={() => setShowCompareModal(false)}
                className="close-modal-btn"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="compare-modal-body">
              <div className={`compare-grid ${
                selectedSessionIds.size === 2 ? 'compare-grid-2' :
                selectedSessionIds.size === 3 ? 'compare-grid-3' :
                'compare-grid-4'
              }`}>
                {Array.from(selectedSessionIds).map((sessionId, index) => {
                  const session = sessions.find(s => s.dbId === sessionId) || allSessions?.find(s => s.dbId === sessionId);
                  if (!session) return null;

                  const gradientColors = [
                    'from-purple-500 to-pink-500',
                    'from-blue-500 to-cyan-500',
                    'from-green-500 to-teal-500',
                    'from-orange-500 to-yellow-500'
                  ];
                  const gradient = gradientColors[index % gradientColors.length];

                  return (
                    <div key={sessionId} className="compare-card">
                      <div className={`compare-card-header bg-gradient-to-r ${gradient}`}>
                        <div className="card-header-content">
                          <h4>{session.title}</h4>
                          <div className="card-meta">
                            <MessageSquare className="w-3 h-3" />
                            <span>{session.messages?.length || 0} 条</span>
                          </div>
                        </div>
                        <div className="card-number">
                          {index + 1}
                        </div>
                      </div>

                      <div className="compare-card-body">
                        {session.messages && session.messages.length > 0 ? (
                          <div className="messages-list">
                            {session.messages.slice(0, 8).map((msg, msgIndex) => (
                              <div
                                key={msg.id || msgIndex}
                                className={`compare-message ${
                                  msg.role === 'user' ? 'message-user' : 'message-ai'
                                }`}
                              >
                                <div className="message-header">
                                  <span className="message-role">
                                    {msg.role === 'user' ? '👤 用户' : '🤖 AI'}
                                  </span>
                                  {msg.timestamp && (
                                    <span className="message-time">
                                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                    </span>
                                  )}
                                </div>
                                <p className="message-text">
                                  {msg.content?.substring(0, 150)}
                                  {msg.content?.length > 150 && '...'}
                                </p>
                              </div>
                            ))}
                            {session.messages.length > 8 && (
                              <div className="more-messages-hint">
                                + {session.messages.length - 8} 条更多消息
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="empty-state-hint">
                            <MessageSquare className="w-8 h-8" />
                            <p>暂无消息</p>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatHistory;