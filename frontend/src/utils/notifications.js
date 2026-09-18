// 通知工具函数
export const requestNotificationPermission = () => {
  if ('Notification' in window) {
    if (Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        console.log('通知权限:', permission);
      });
    }
  } else {
    console.warn('当前浏览器不支持通知');
  }
};

export const showNotification = (title, options = {}) => {
  if (!('Notification' in window)) {
    console.warn('当前浏览器不支持通知');
    return;
  }

  if (Notification.permission === 'granted') {
    const notification = new Notification(title, {
      icon: '/logo.png',
      badge: '/logo.png',
      ...options
    });

    // 自动关闭通知（5秒后）
    setTimeout(() => {
      notification.close();
    }, 5000);

    return notification;
  } else if (Notification.permission !== 'denied') {
    Notification.requestPermission().then(permission => {
      if (permission === 'granted') {
        showNotification(title, options);
      }
    });
  }
};

export const notifyNewMessage = (message) => {
  showNotification('新消息', {
    body: message.content?.substring(0, 100) + (message.content?.length > 100 ? '...' : ''),
    tag: 'new-message'
  });
};

export const notifyCartAction = (productName, action) => {
  const actionText = action === 'added' ? '已添加到购物车' : '已从购物车移除';
  showNotification('购物车更新', {
    body: `${productName} ${actionText}`,
    tag: 'cart-action'
  });
};

export const notifyWishlistAction = (productName, action) => {
  const actionText = action === 'added' ? '已添加到收藏' : '已从收藏移除';
  showNotification('收藏更新', {
    body: `${productName} ${actionText}`,
    tag: 'wishlist-action'
  });
};

export const notifyAnalysisReady = () => {
  showNotification('数据分析完成', {
    body: '数据分析报告已生成',
    tag: 'analysis-ready'
  });
};
