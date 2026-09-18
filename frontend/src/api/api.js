// API配置
const API_BASE_URL = 'http://localhost:8000';

/**
 * 发送聊天消息
 */
export async function sendMessage(data) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取聊天会话列表
 */
export async function getChatSessions(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to fetch sessions');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 创建新的聊天会话
 */
export async function createChatSession(data = {}) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to create session');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取会话消息（通过数据库ID）
 */
export async function getChatMessages(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}/messages`);
    if (!response.ok) throw new Error('Failed to fetch messages');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取会话消息（通过session_id字符串UUID）
 */
export async function getChatMessagesByUuid(sessionUuid) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/session/by-uuid/${sessionUuid}/messages`);
    if (!response.ok) throw new Error('Failed to fetch messages');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 删除会话
 */
export async function deleteChatSession(sessionId) {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${sessionId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete session');
    return true;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 批量删除会话
 */
export async function deleteChatSessions(sessionIds) {
  try {
    const requestBody = { session_ids: sessionIds };
    console.log('Delete sessions request:', JSON.stringify(requestBody));

    const response = await fetch(`${API_BASE_URL}/chat/sessions/batch`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response:', errorText);
      throw new Error('Failed to delete sessions');
    }
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 搜索商品
 */
export async function searchProducts(params = {}) {
  try {
    const queryString = new URLSearchParams(params).toString();
    const response = await fetch(`${API_BASE_URL}/products?${queryString}`);
    if (!response.ok) throw new Error('Failed to search products');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取商品详情
 */
export async function getProduct(productId) {
  try {
    const response = await fetch(`${API_BASE_URL}/products/${productId}`);
    if (!response.ok) throw new Error('Failed to get product');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 提交反馈
 */
export async function submitFeedback(data) {
  try {
    const response = await fetch(`${API_BASE_URL}/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to submit feedback');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 健康检查
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error('Health check failed');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取购物车
 */
export async function getCart(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/cart?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to get cart');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 添加商品到购物车
 */
export async function addToCart(userId, productId, quantity = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/items?user_id=${userId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        product_id: productId,
        quantity: quantity
      }),
    });
    if (!response.ok) throw new Error('Failed to add to cart');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 更新购物车商品数量
 */
export async function updateCartItemQuantity(userId, itemId, quantity) {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}?user_id=${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ quantity }),
    });
    if (!response.ok) throw new Error('Failed to update cart item');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 从购物车移除商品
 */
export async function removeCartItem(userId, itemId) {
  try {
    const response = await fetch(`${API_BASE_URL}/cart/items/${itemId}?user_id=${userId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove cart item');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 清空购物车
 */
export async function clearCart(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/cart?user_id=${userId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to clear cart');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取收藏列表
 */
export async function getWishlist(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to get wishlist');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 添加商品到收藏
 */
export async function addToWishlist(userId, productId) {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/${productId}?user_id=${userId}`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to add to wishlist');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 从收藏移除商品
 */
export async function removeFromWishlist(userId, productId) {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/${productId}?user_id=${userId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to remove from wishlist');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 检查商品是否在收藏中
 */
export async function checkProductInWishlist(userId, productId) {
  try {
    const response = await fetch(`${API_BASE_URL}/wishlist/check/${productId}?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to check wishlist');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 导出对话历史
 */
export async function exportChatHistory(sessionId, format = 'txt') {
  try {
    const response = await fetch(`${API_BASE_URL}/chat/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        format: format
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(errorText || 'Failed to export chat history');
    }

    // 下载文件
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = response.headers.get('Content-Disposition')?.match(/filename=(.+)/)?.[1] || `chat_history.${format}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    return { success: true };
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取综合分析报告
 */
export async function getAnalyticsReport(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/overview?user_id=${userId}`);
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`获取分析报告失败 (Status: ${response.status}):`, errorText);
      throw new Error(errorText || 'Failed to get analytics report');
    }
    const data = await response.json();
    console.log('分析报告数据:', data);
    return data;
  } catch (error) {
    console.error('API Error - getAnalyticsReport:', error);
    throw error;
  }
}

/**
 * 获取会话统计
 */
export async function getSessionStatistics(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/sessions?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to get session statistics');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取用户行为统计
 */
export async function getUserBehaviorStatistics(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/behavior?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to get user behavior statistics');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取热门商品排行
 */
export async function getTopProducts(userId = 1, limit = 10) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/top-products?user_id=${userId}&limit=${limit}`);
    if (!response.ok) throw new Error('Failed to get top products');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 获取意图分布
 */
export async function getIntentDistribution(userId = 1) {
  try {
    const response = await fetch(`${API_BASE_URL}/analytics/intents?user_id=${userId}`);
    if (!response.ok) throw new Error('Failed to get intent distribution');
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
}

/**
 * 导出分析报告
 */
export async function exportAnalyticsReport(userId = 1) {
  try {
    console.log(`开始导出分析报告 (userId: ${userId})`);
    const response = await fetch(`${API_BASE_URL}/analytics/export?user_id=${userId}`);

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`导出分析报告失败 (Status: ${response.status}):`, errorText);
      throw new Error(errorText || 'Failed to export analytics report');
    }

    // 下载文件
    const blob = await response.blob();
    console.log('文件下载完成，大小:', blob.size, 'bytes');
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = response.headers.get('Content-Disposition')?.match(/filename=(.+)/)?.[1] || `analytics_report_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);

    console.log('文件下载成功');
    return { success: true };
  } catch (error) {
    console.error('API Error - exportAnalyticsReport:', error);
    throw error;
  }
}