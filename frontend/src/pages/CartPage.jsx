import React, { useState, useEffect } from 'react';
import { ShoppingBag, Trash2, Minus, Plus, ArrowLeft, ChevronRight } from 'lucide-react';
import { getCart, removeCartItem, updateCartItemQuantity, clearCart } from '../api/api';

function CartPage({ onBack }) {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [totalPrice, setTotalPrice] = useState(0);

  useEffect(() => {
    loadCart();
  }, []);

  useEffect(() => {
    calculateTotal();
  }, [cartItems, selectedItems]);

  const loadCart = async () => {
    try {
      setLoading(true);
      const response = await getCart(1);

      let items = [];
      if (Array.isArray(response)) {
        items = response;
      } else if (response && response.items && Array.isArray(response.items)) {
        items = response.items;
      } else if (response && typeof response === 'object') {
        items = Object.values(response).filter(item => item && typeof item === 'object');
      }

      setCartItems(items);
    } catch (error) {
      console.error('加载购物车失败:', error);
      setCartItems([]);
    } finally {
      setLoading(false);
    }
  };

  const calculateTotal = () => {
    const total = cartItems
      .filter(item => selectedItems.has(item.id))
      .reduce((sum, item) => sum + item.product.price * item.quantity, 0);
    setTotalPrice(total);
  };

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedItems(new Set(cartItems.map(item => item.id)));
    } else {
      setSelectedItems(new Set());
    }
  };

  const handleSelectItem = (itemId, checked) => {
    const newSelected = new Set(selectedItems);
    checked ? newSelected.add(itemId) : newSelected.delete(itemId);
    setSelectedItems(newSelected);
  };

  const handleUpdateQuantity = async (itemId, newQuantity) => {
    if (newQuantity < 1) return;
    try {
      await updateCartItemQuantity(1, itemId, newQuantity);
      setCartItems(cartItems.map(item =>
        item.id === itemId ? { ...item, quantity: newQuantity } : item
      ));
    } catch (error) {
      console.error('更新数量失败:', error);
    }
  };

  const handleRemoveItem = async (itemId) => {
    if (!window.confirm('确定要删除这个商品吗？')) return;
    try {
      await removeCartItem(1, itemId);
      setCartItems(cartItems.filter(item => item.id !== itemId));
      setSelectedItems(prev => {
        const s = new Set(prev);
        s.delete(itemId);
        return s;
      });
    } catch (error) {
      console.error('删除商品失败:', error);
    }
  };

  const handleClearCart = async () => {
    if (!window.confirm('确定要清空购物车吗？')) return;
    try {
      await clearCart(1);
      setCartItems([]);
      setSelectedItems(new Set());
    } catch (error) {
      console.error('清空购物车失败:', error);
    }
  };

  const handleCheckout = () => {
    if (selectedItems.size === 0) {
      alert('请先选择要结算的商品');
      return;
    }
    alert(`结算金额: ¥${totalPrice.toFixed(2)}\n功能开发中...`);
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
    <div className="page-container cart-page">
      {/* 顶部导航 */}
      <div className="page-header">
        <button className="back-button" onClick={onBack}>
          <ArrowLeft className="w-5 h-5" />
          返回
        </button>
        <h1 className="page-title">
          <ShoppingBag className="w-6 h-6" />
          购物车 ({cartItems.length})
        </h1>
      </div>

      <div className="cart-content">
        {cartItems.length === 0 ? (
          /* ✅ 这里只删掉了巨大的购物车图标，其它不动 */
          <div className="empty-cart">
            <h2>购物车是空的</h2>
            <p>快去选购心仪的商品吧</p>
            <button className="primary-button" onClick={onBack}>
              去购物
            </button>
          </div>
        ) : (
          <>
            {/* 工具栏 */}
            <div className="cart-toolbar">
              <label className="select-all">
                <input
                  type="checkbox"
                  checked={selectedItems.size === cartItems.length && cartItems.length > 0}
                  onChange={(e) => handleSelectAll(e.target.checked)}
                />
                <span>全选</span>
              </label>
              <button className="text-button danger" onClick={handleClearCart}>
                <Trash2 className="w-4 h-4" />
                清空购物车
              </button>
            </div>

            {/* 商品列表 */}
            <div className="cart-items">
              {cartItems.map((item) => (
                <div key={item.id} className="cart-item">
                  <div className="item-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedItems.has(item.id)}
                      onChange={(e) => handleSelectItem(item.id, e.target.checked)}
                    />
                  </div>

                  <div className="item-image">
                    <img src={item.product.image_url} alt={item.product.name} />
                  </div>

                  <div className="item-info">
                    <h4 className="item-name">{item.product.name}</h4>
                    <p className="item-category">{item.product.category}</p>
                    <div className="item-price">¥{item.product.price.toFixed(2)}</div>
                  </div>

                  <div className="item-quantity">
                    <button onClick={() => handleUpdateQuantity(item.id, item.quantity - 1)}>
                      <Minus />
                    </button>
                    <span>{item.quantity}</span>
                    <button onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}>
                      <Plus />
                    </button>
                  </div>

                  <div className="item-total">
                    ¥{(item.product.price * item.quantity).toFixed(2)}
                  </div>

                  <button className="item-delete" onClick={() => handleRemoveItem(item.id)}>
                    <Trash2 />
                  </button>
                </div>
              ))}
            </div>

            {/* 结算栏 */}
            <div className="cart-footer">
              <div>已选 {selectedItems.size} 件</div>
              <div>
                合计 ¥{totalPrice.toFixed(2)}
                <button className="checkout-button" onClick={handleCheckout}>
                  去结算 <ChevronRight />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default CartPage;
