import React, { useState, useEffect } from 'react';
import { Heart, ShoppingBag, Trash2, ArrowLeft, Grid, List } from 'lucide-react';
import { getWishlist, removeFromWishlist } from '../api/api';

function WishlistPage({ onBack }) {
  const [wishlistItems, setWishlistItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [selectedItems, setSelectedItems] = useState(new Set());

  useEffect(() => {
    loadWishlist();
  }, []);

  const loadWishlist = async () => {
    try {
      setLoading(true);
      const response = await getWishlist(1);

      // 确保返回的是数组格式
      let items = [];
      if (Array.isArray(response)) {
        items = response;
      } else if (response && response.items && Array.isArray(response.items)) {
        items = response.items;
      } else if (response && typeof response === 'object') {
        // 如果返回的是对象，尝试转换为数组
        console.log('API返回数据格式:', response);
        items = Object.values(response).filter(item => item && typeof item === 'object');
      }

      setWishlistItems(items);
    } catch (error) {
      console.error('加载收藏失败:', error);
      setWishlistItems([]); // 确保出错时设置为空数组
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!window.confirm('确定要取消收藏这个商品吗？')) return;
    try {
      await removeFromWishlist(1, itemId);
      setWishlistItems(wishlistItems.filter(item => item.product.id !== itemId));
    } catch (error) {
      console.error('取消收藏失败:', error);
    }
  };

  const handleBatchDelete = async () => {
    if (selectedItems.size === 0) {
      alert('请先选择要删除的商品');
      return;
    }
    if (!window.confirm(`确定要删除选中的 ${selectedItems.size} 个商品吗？`)) return;

    try {
      const deletePromises = Array.from(selectedItems).map(itemId =>
        removeFromWishlist(1, itemId)
      );
      await Promise.all(deletePromises);

      setWishlistItems(wishlistItems.filter(item =>
        !selectedItems.has(item.product.id)
      ));
      setSelectedItems(new Set());
    } catch (error) {
      console.error('批量删除失败:', error);
    }
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedItems(new Set(wishlistItems.map(item => item.product.id)));
    } else {
      setSelectedItems(new Set());
    }
  };

  const handleSelectItem = (productId, checked) => {
    const newSelected = new Set(selectedItems);
    if (checked) {
      newSelected.add(productId);
    } else {
      newSelected.delete(productId);
    }
    setSelectedItems(newSelected);
  };

  if (loading) {
    return (
      <div className="page-container">
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container wishlist-page">
      {/* 顶部导航 */}
      <div className="page-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft className="w-5 h-5" />
          返回
        </button>
        <h1 className="page-title">
          <Heart className="w-6 h-6" />
          我的收藏 ({wishlistItems.length})
        </h1>
      </div>

      {/* 收藏内容 */}
      <div className="wishlist-content">
        {wishlistItems.length === 0 ? (
          <div className="empty-wishlist">
            <Heart className="w-24 h-24 text-gray-300" />
            <h2>暂无收藏商品</h2>
            <p>去收藏喜欢的商品吧</p>
            <button className="primary-button" onClick={onBack}>
              去逛逛
            </button>
          </div>
        ) : (
          <>
            {/* 工具栏 */}
            <div className="wishlist-toolbar">
              <div className="toolbar-left">
                <label className="select-all">
                  <input
                    type="checkbox"
                    checked={selectedItems.size === wishlistItems.length && wishlistItems.length > 0}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                  />
                  <span>全选</span>
                </label>
                {selectedItems.size > 0 && (
                  <span className="selected-count">
                    已选 {selectedItems.size} 件
                  </span>
                )}
              </div>
              <div className="toolbar-right">
                <button
                  className={`view-toggle ${viewMode === 'grid' ? 'active' : ''}`}
                  onClick={() => setViewMode('grid')}
                  title="网格视图"
                >
                  <Grid className="w-5 h-5" />
                </button>
                <button
                  className={`view-toggle ${viewMode === 'list' ? 'active' : ''}`}
                  onClick={() => setViewMode('list')}
                  title="列表视图"
                >
                  <List className="w-5 h-5" />
                </button>
                {selectedItems.size > 0 && (
                  <button className="text-button danger" onClick={handleBatchDelete}>
                    <Trash2 className="w-4 h-4" />
                    删除选中
                  </button>
                )}
              </div>
            </div>

            {/* 商品列表 */}
            <div className={`wishlist-items ${viewMode}`}>
              {wishlistItems.map((item) => (
                <div key={item.id} className="wishlist-item">
                  <div className="item-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(item.product.id)}
                      onChange={(e) => handleSelectItem(item.product.id, e.target.checked)}
                    />
                  </div>

                  <div className="item-content">
                    <div className="item-image">
                      <img
                        src={item.product.image_url}
                        alt={item.product.name}
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                      <div className="item-actions">
                        <button
                          className="action-button"
                          onClick={() => handleRemoveItem(item.product.id)}
                          title="删除"
                        >
                          <Trash2 className="w-5 h-5" />
                        </button>
                      </div>
                    </div>

                    <div className="item-info">
                      <h4 className="item-name">{item.product.name}</h4>
                      <p className="item-category">{item.product.category}</p>
                      <div className="item-price">¥{item.product.price.toFixed(2)}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default WishlistPage;
