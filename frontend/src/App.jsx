import React, { useState, useEffect } from 'react';
import ChatWindow from './components/ChatWindow';
import ChatHistory from './components/ChatHistory';
import CartPage from './pages/CartPage';
import WishlistPage from './pages/WishlistPage';
import AnalyticsPage from './pages/AnalyticsPage';
import { getChatSessions, createChatSession, getChatMessages, deleteChatSessions } from './api/api';
import { requestNotificationPermission, notifyAnalysisReady } from './utils/notifications';
import './styles/App.css';
import './styles/Pages.css';

function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState('chat'); // 'chat', 'cart', 'wishlist', 'analytics'
  const [sidebarWidth, setSidebarWidth] = useState(280); // 侧边栏宽度
  const [isResizing, setIsResizing] = useState(false); // 是否正在拖动调整大小

  // 保存状态到 localStorage
  const saveAppState = () => {
    const state = {
      currentSessionId: currentSession?.id,
      currentPage: currentPage,
      sidebarOpen: sidebarOpen,
      sidebarWidth: sidebarWidth,
      sessions: sessions  // 添加会话列表的保存
    };
    localStorage.setItem('appState', JSON.stringify(state));
  };

  // 从 localStorage 加载状态
  const loadAppState = () => {
    try {
      const savedState = localStorage.getItem('appState');
      if (savedState) {
        const state = JSON.parse(savedState);
        setCurrentPage(state.currentPage || 'chat');
        setSidebarOpen(state.sidebarOpen !== false);
        setSidebarWidth(state.sidebarWidth || 280);

        // 确保缓存的会话有正确的结构
        const cachedSessions = (state.sessions || []).map(session => ({
          ...session,
          // 如果会话有消息，标记为已加载
          messagesLoaded: session.messages && session.messages.length > 0
        }));

        // 返回会话ID和缓存的会话列表
        return {
          savedSessionId: state.currentSessionId,
          cachedSessions: cachedSessions
        };
      }
    } catch (error) {
      console.error('加载应用状态失败:', error);
    }
    return { savedSessionId: null, cachedSessions: [] };
  };

  // 加载会话列表
  useEffect(() => {
    const { savedSessionId, cachedSessions } = loadAppState();
    // 如果有缓存的会话，先设置到状态
    if (cachedSessions && cachedSessions.length > 0) {
      setSessions(cachedSessions);
    }
    // 然后加载会话（此时sessions已经有值了）
    loadSessions(savedSessionId, cachedSessions);
    // 请求通知权限
    requestNotificationPermission();
  }, []);

  // 监听状态变化并保存
  useEffect(() => {
    saveAppState();
  }, [currentSession, currentPage, sidebarOpen, sidebarWidth, sessions]);

  // 监听页面变化
  useEffect(() => {
    if (currentPage === 'analytics') {
      notifyAnalysisReady();
    }
  }, [currentPage]);

  const loadSessions = async (savedSessionId = null, cachedSessions = []) => {
    try {
      setLoading(true);

      // 如果有缓存的会话，先使用缓存的数据
      if (cachedSessions && cachedSessions.length > 0) {
        console.log('使用本地缓存的会话数据');
        setSessions(cachedSessions);

        // 尝试恢复之前选中的会话
        if (savedSessionId) {
          const savedSession = cachedSessions.find(s => s.id === savedSessionId);
          if (savedSession) {
            await selectSession(savedSession);
          } else if (cachedSessions.length > 0) {
            await selectSession(cachedSessions[0]);
          }
        } else if (cachedSessions.length > 0) {
          await selectSession(cachedSessions[0]);
        }
        // 不再调用后台同步，避免覆盖已加载的消息
        console.log('跳过后台同步，保留已加载的消息');
      } else {
        // 如果没有缓存，从后端加载
        console.log('从后端加载会话数据');
        const sessionsData = await getChatSessions(1);
        // 将后端返回的会话数据转换为前端格式
        const formattedSessions = sessionsData.map(session => ({
          id: session.session_id,
          dbId: session.id,
          title: session.title || `会话 ${new Date(session.created_at).toLocaleString()}`,
          messages: [], // 消息会在选择会话时加载
          createdAt: session.created_at,
          updatedAt: session.updated_at
        }));
        setSessions(formattedSessions);

        // 如果有会话，尝试恢复保存的会话或选择第一个
        if (formattedSessions.length > 0) {
          if (savedSessionId) {
            const savedSession = formattedSessions.find(s => s.id === savedSessionId);
            if (savedSession) {
              await selectSession(savedSession);
            } else {
              await selectSession(formattedSessions[0]);
            }
          } else {
            await selectSession(formattedSessions[0]);
          }
        } else {
          // 如果没有会话，创建新会话
          await handleNewSession();
        }
      }
    } catch (error) {
      console.error('加载会话列表失败:', error);
      // 如果加载失败，但已有缓存会话，则不创建新会话
      if (cachedSessions.length === 0) {
        await handleNewSession();
      }
    } finally {
      setLoading(false);
    }
  };

  // 从后端同步会话列表（后台同步）
  const syncSessionsFromBackend = async () => {
    try {
      console.log('后台同步会话数据...');
      const sessionsData = await getChatSessions(1);
      const formattedSessions = sessionsData.map(session => ({
        id: session.session_id,
        dbId: session.id,
        title: session.title || `会话 ${new Date(session.created_at).toLocaleString()}`,
        messages: [],
        createdAt: session.created_at,
        updatedAt: session.updated_at
      }));
      
      // 更新会话列表（如果数据有变化）
      setSessions(formattedSessions);
      console.log('会话数据同步完成');
    } catch (error) {
      console.error('后台同步会话数据失败:', error);
    }
  };

  const handleNewSession = async () => {
    try {
      // 调用后端创建会话
      const newSessionData = await createChatSession({
        title: null // 让后端自动生成标题
      });

      const newSession = {
        id: newSessionData.session_id,
        dbId: newSessionData.id,
        title: newSessionData.title || `新会话 ${sessions.length + 1}`,
        messages: [],
        createdAt: newSessionData.created_at,
        updatedAt: newSessionData.updatedAt
      };

      setSessions([...sessions, newSession]);
      setCurrentSession(newSession);
    } catch (error) {
      console.error('创建会话失败:', error);
      // 如果创建失败，使用前端临时会话
      const newSession = {
        id: String(Date.now()),
        title: `新会话 ${sessions.length + 1}`,
        messages: [],
        isTemporary: true
      };
      setSessions([...sessions, newSession]);
      setCurrentSession(newSession);
    }
  };

  const selectSession = async (session) => {
    setCurrentSession(session);

    // 如果会话还没有加载消息，则从后端加载
    // 但如果会话已经有消息且标记为已加载，则跳过
    if (session && !session.messagesLoaded && !session.isTemporary && !session.messages) {
      try {
        const messages = await getChatMessages(session.dbId); // 使用数据库ID
        const formattedMessages = messages.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          intent: msg.intent,
          confidence: msg.confidence,
          timestamp: msg.created_at,
          // ✅ 修复：更强的容错处理
          retrieved_docs: (() => {
            // 如果没有数据，返回 null
            if (!msg.retrieved_docs) {
              return null;
            }

            // 如果已经是对象/数组，直接返回
            if (typeof msg.retrieved_docs === 'object' && msg.retrieved_docs !== null) {
              console.log('retrieved_docs 已是对象，直接返回');
              return msg.retrieved_docs;
            }

            // 如果是字符串，尝试解析
            if (typeof msg.retrieved_docs === 'string') {
              const strData = msg.retrieved_docs.trim();
              console.log('尝试解析 retrieved_docs 字符串:', strData.substring(0, 100) + '...');

              // 尝试 JSON.parse
              try {
                const parsed = JSON.parse(strData);
                console.log('JSON.parse 成功');
                return parsed;
              } catch (e) {
                console.warn('JSON.parse 失败，可能是 Python 格式的字符串');
                // Python 格式使用单引号，JSON 需要双引号
                // 尝试将单引号替换为双引号后再解析
                try {
                  const converted = strData.replace(/'/g, '"');
                  const parsed = JSON.parse(converted);
                  console.log('转换单引号后解析成功');
                  return parsed;
                } catch (e2) {
                  console.error('解析 retrieved_docs 完全失败:', e2, '原始数据:', msg.retrieved_docs);
                  return null;
                }
              }
            }

            // 其他类型，返回 null
            console.warn('retrieved_docs 类型未知:', typeof msg.retrieved_docs);
            return null;
          })()
        }));

        // 更新会话的消息
        const updatedSession = {
          ...session,
          messages: formattedMessages,
          messagesLoaded: true
        };

        setCurrentSession(updatedSession);
        setSessions(sessions.map(s =>
          s.id === session.id ? updatedSession : s
        ));
      } catch (error) {
        console.error('加载会话消息失败:', error);
      }
    }
  };

  const handleSelectSession = (session) => {
    selectSession(session);
  };

  const handleDeleteSessions = async (sessionIds) => {
    try {
      await deleteChatSessions(sessionIds);

      // 从前端状态中删除这些会话
      const updatedSessions = sessions.filter(s => !sessionIds.includes(s.dbId));
      setSessions(updatedSessions);

      // 如果删除的会话包含当前会话，切换到其他会话或创建新会话
      if (currentSession && sessionIds.includes(currentSession.dbId)) {
        if (updatedSessions.length > 0) {
          await selectSession(updatedSessions[0]);
        } else {
          await handleNewSession();
        }
      }
    } catch (error) {
      console.error('删除会话失败:', error);
      throw error;
    }
  };

  const handleUpdateSession = (updatedSession) => {
    // 更新会话标题（使用第一条用户消息）
    if (!updatedSession.title) {
      const firstUserMessage = updatedSession.messages.find(
        msg => msg.role === 'user'
      );
      if (firstUserMessage) {
        updatedSession.title = firstUserMessage.content.substring(0, 30) +
          (firstUserMessage.content.length > 30 ? '...' : '');
      }
    }

    setSessions(sessions.map(s =>
      s.id === updatedSession.id ? updatedSession : s
    ));
    setCurrentSession(updatedSession);
  };

  // 根据当前页面渲染不同内容
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'cart':
        return <CartPage onBack={() => setCurrentPage('chat')} />;
      case 'wishlist':
        return <WishlistPage onBack={() => setCurrentPage('chat')} />;
      case 'analytics':
        return <AnalyticsPage onBack={() => setCurrentPage('chat')} />;
      default:
        return (
          <ChatWindow
            session={currentSession}
            onUpdateSession={handleUpdateSession}
            onNavigateToCart={() => setCurrentPage('cart')}
            onNavigateToWishlist={() => setCurrentPage('wishlist')}
          />
        );
    }
  };

  // 侧边栏拖动调整大小的处理函数
  const handleMouseDown = (e) => {
    e.preventDefault();
    setIsResizing(true);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseMove = (e) => {
    if (!isResizing) return;
    const newWidth = e.clientX;
    // 限制最小和最大宽度
    const minWidth = 200;
    const maxWidth = 600;
    const clampedWidth = Math.max(minWidth, Math.min(maxWidth, newWidth));
    setSidebarWidth(clampedWidth);
  };

  const handleMouseUp = () => {
    setIsResizing(false);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="logo">
          <span className="logo-icon">🛒</span>
          <h1>智能电商客服</h1>
        </div>
        {currentPage === 'chat' && (
          <div className="header-actions">
            <button
              className="new-chat-btn"
              onClick={handleNewSession}
            >
              + 新对话
            </button>
            <button
              className="analytics-btn"
              onClick={() => setCurrentPage('analytics')}
            >
              📊 数据分析
            </button>
          </div>
        )}
      </header>

      <div className="app-container">
        {currentPage === 'chat' && sidebarOpen && (
          <aside className="sidebar" style={{ width: `${sidebarWidth}px` }}>
            <ChatHistory
              sessions={sessions}
              allSessions={sessions}
              currentSession={currentSession}
              onSelectSession={handleSelectSession}
              onDeleteSessions={handleDeleteSessions}
            />
          </aside>
        )}

        {/* 拖动调整大小的分割条 */}
        {currentPage === 'chat' && sidebarOpen && (
          <div
            className={`resize-handle ${isResizing ? 'resizing' : ''}`}
            onMouseDown={handleMouseDown}
            title="拖动调整宽度"
          >
            <div className="resize-line"></div>
          </div>
        )}

        <main className="main-content">
          {renderCurrentPage()}
        </main>
      </div>
    </div>
  );
}

export default App;