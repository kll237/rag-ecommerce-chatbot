import { useState, useEffect } from 'react';
import { X, Trash2, ShoppingBag, Plus, Minus, CheckSquare, Square, ChevronRight, AlertCircle, Store, Tag, Package } from 'lucide-react';

const CartModal = ({ isOpen, onClose, session_id, API_BASE_URL }) => {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [editingQuantities, setEditingQuantities] = useState({});
  const [isEditingQuantity, setIsEditingQuantity] = useState(false);
  const [hoveredItem, setHoveredItem] = useState(null);

  const fetchCart = async () => {
    try {
      setLoading(true);
      setError(null);
      const url = session_id
        ? `${API_BASE_URL}/cart?user_id=1&session_id=${session_id}`
        : `${API_BASE_URL}/cart?user_id=1`;

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error('获取购物车失败');
      }
      const data = await response.json();
      setCart(data);
      // 默认选中所有商品
      if (data.items && data.items.length > 0) {
        const initialSelected = new Set(data.items.map(item => item.id));
        setSelectedItems(initialSelected);

        // 初始化编辑数量状态
        const initialEditingQuantities = {};
        data.items.forEach(item => {
          initialEditingQuantities[item.id] = item.quantity;
        });
        setEditingQuantities(initialEditingQuantities);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = async (productId, newQuantity) => {
    if (newQuantity < 1) return;

    try {
      const url = session_id
        ? `${API_BASE_URL}/cart/items/${productId}?user_id=1&session_id=${session_id}&quantity=${newQuantity}`
        : `${API_BASE_URL}/cart/items/${productId}?user_id=1&quantity=${newQuantity}`;

      const response = await fetch(url, {
        method: 'PUT',
      });
      if (!response.ok) {
        throw new Error('更新数量失败');
      }
      await fetchCart();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleQuantityInput = (itemId, value) => {
    const numValue = parseInt(value, 10);
    if (!isNaN(numValue) && numValue >= 1 && numValue <= 99) {
      setEditingQuantities(prev => ({
        ...prev,
        [itemId]: numValue
      }));
    }
  };

  const handleQuantityBlur = async (itemId) => {
    const newQuantity = editingQuantities[itemId];
    if (newQuantity && newQuantity >= 1) {
      setIsEditingQuantity(true);
      await updateQuantity(itemId, newQuantity);
      setIsEditingQuantity(false);
    }
  };

  const removeItem = async (productId) => {
    if (!confirm('确定要从购物车移除该商品吗？')) return;

    try {
      const url = session_id
        ? `${API_BASE_URL}/cart/items/${productId}?user_id=1&session_id=${session_id}`
        : `${API_BASE_URL}/cart/items/${productId}?user_id=1`;

      const response = await fetch(url, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('移除商品失败');
      }
      await fetchCart();
    } catch (err) {
      alert(err.message);
    }
  };

  const clearCart = async () => {
    if (!confirm('确定要清空购物车吗？')) return;

    try {
      const url = session_id
        ? `${API_BASE_URL}/cart?user_id=1&session_id=${session_id}`
        : `${API_BASE_URL}/cart?user_id=1`;

      const response = await fetch(url, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('清空购物车失败');
      }
      await fetchCart();
    } catch (err) {
      alert(err.message);
    }
  };

  const toggleSelectAll = () => {
    if (!cart || cart.items.length === 0) return;

    if (selectedItems.size === cart.items.length) {
      setSelectedItems(new Set());
    } else {
      setSelectedItems(new Set(cart.items.map(item => item.id)));
    }
  };

  const toggleSelectItem = (itemId) => {
    const newSelected = new Set(selectedItems);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedItems(newSelected);
  };

  const getSelectedTotal = () => {
    if (!cart) return { quantity: 0, price: 0 };

    let totalQuantity = 0;
    let totalPrice = 0;

    cart.items.forEach(item => {
      if (selectedItems.has(item.id)) {
        totalQuantity += item.quantity;
        totalPrice += (item.product?.price || 0) * item.quantity;
      }
    });

    return { quantity: totalQuantity, price: totalPrice };
  };

  const { quantity: selectedQuantity, price: selectedPrice } = getSelectedTotal();

  useEffect(() => {
    if (isOpen) {
      fetchCart();
    }
  }, [isOpen, session_id]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col animate-slide-up overflow-hidden">
        {/* 标题栏 - 淘宝风格 */}
        <div className="sticky top-0 z-10 bg-gradient-to-r from-orange-500 to-red-500 p-5 flex-shrink-0">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="relative">
                <ShoppingBag className="w-8 h-8 text-white" />
                {cart && cart.items.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-yellow-400 text-red-600 text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center border-2 border-white shadow-lg">
                    {cart.items.length}
                  </span>
                )}
              </div>
              <div>
                <h2 className="text-xl font-bold text-white tracking-wide">我的购物车</h2>
                {cart && cart.items.length > 0 && (
                  <p className="text-xs text-white/80 mt-0.5">
                    已选 <span className="text-yellow-300 font-bold">{selectedQuantity}</span> / 共 {cart.items.length} 件商品
                  </p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchCart}
                className="text-white/80 hover:text-white p-2 rounded-full hover:bg-white/20 transition-all active:scale-95"
                title="刷新购物车"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              </button>
              <button
                onClick={onClose}
                className="text-white/80 hover:text-white p-2 rounded-full hover:bg-white/20 transition-all active:scale-95"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        {/* 全选栏 */}
        {cart && cart.items.length > 0 && (
          <div className="sticky top-[84px] z-10 flex items-center justify-between px-5 py-3 bg-gray-50 border-b border-gray-100 flex-shrink-0">
            <button
              onClick={toggleSelectAll}
              className="flex items-center gap-2.5 text-sm text-gray-700 hover:text-orange-500 transition-colors group"
            >
              {selectedItems.size === cart.items.length ? (
                <div className="flex items-center justify-center w-5 h-5 bg-gradient-to-br from-orange-500 to-red-500 text-white rounded shadow-sm">
                  <CheckSquare className="w-3.5 h-3.5" />
                </div>
              ) : (
                <div className="w-5 h-5 border-2 border-gray-300 rounded group-hover:border-orange-400 transition-colors" />
              )}
              <span className="font-medium">全选</span>
            </button>

            <div className="flex items-center gap-4">
              <button
                onClick={clearCart}
                className="text-sm text-gray-500 hover:text-red-500 transition-colors flex items-center gap-1.5 group"
              >
                <Trash2 className="w-4 h-4 group-hover:scale-110 transition-transform" />
                <span>清空购物车</span>
              </button>
            </div>
          </div>
        )}

        {/* 内容区 */}
        <div className="flex-1 overflow-y-auto bg-gray-50">
          {loading ? (
            <div className="flex flex-col items-center justify-center h-80">
              <div className="relative mb-6">
                <div className="w-20 h-20 border-4 border-orange-100 rounded-full" />
                <div className="absolute inset-0 w-20 h-20 border-4 border-transparent border-t-orange-500 rounded-full animate-spin" />
                <ShoppingBag className="absolute inset-0 m-auto w-10 h-10 text-orange-400" />
              </div>
              <p className="text-gray-500 font-medium">加载购物车中...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center h-80 text-red-500 p-8">
              <AlertCircle className="w-16 h-16 mb-4 text-red-400" />
              <p className="text-center font-medium">{error}</p>
              <button
                onClick={fetchCart}
                className="mt-6 px-6 py-2.5 bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-lg hover:from-orange-600 hover:to-red-600 transition-all shadow-lg hover:shadow-xl active:scale-95"
              >
                重新加载
              </button>
            </div>
          ) : !cart || cart.items.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-80 p-8">
              <div className="relative mb-8">
                <div className="w-32 h-32 bg-gradient-to-br from-orange-50 to-red-50 rounded-full flex items-center justify-center">
                  <ShoppingBag className="w-16 h-16 text-orange-200" />
                </div>
                <div className="absolute -bottom-2 -right-2 w-12 h-12 bg-white rounded-full shadow-lg flex items-center justify-center">
                  <span className="text-2xl">😊</span>
                </div>
              </div>
              <p className="text-xl font-bold text-gray-800 mb-2">购物车是空的</p>
              <p className="text-sm text-gray-500 text-center mb-6">快去选购心仪的商品吧</p>
              <div className="flex items-center gap-2 text-sm text-gray-400">
                <span>点击商品图片或</span>
                <span className="px-3 py-1 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs rounded-full font-medium shadow-md">
                  加入购物车
                </span>
                <span>按钮</span>
              </div>
            </div>
          ) : (
            <div className="p-4 space-y-3">
              {/* 店铺分组 */}
              <div className="bg-white rounded-xl shadow-sm overflow-hidden">
                {/* 店铺头部 */}
                <div className="bg-gradient-to-r from-orange-50 to-red-50 px-4 py-2.5 flex items-center gap-2 border-b border-orange-100">
                  <Store className="w-4 h-4 text-orange-500" />
                  <span className="text-sm font-medium text-gray-800">官方店铺</span>
                  <span className="text-xs text-gray-400 ml-auto">官方自营</span>
                </div>

                {/* 商品列表 */}
                <div className="divide-y divide-gray-50">
                  {cart.items.map((item) => {
                    const isOutOfStock = item.product?.stock === 0;
                    const isLowStock = item.product?.stock && item.product.stock < 10 && item.product.stock > 0;

                    return (
                      <div
                        key={item.id}
                        className={`group relative transition-all duration-300 ${
                          selectedItems.has(item.id)
                            ? 'bg-gradient-to-r from-orange-50/50 to-red-50/50'
                            : 'hover:bg-gray-50'
                        } ${isOutOfStock ? 'opacity-60' : ''}`}
                        onMouseEnter={() => setHoveredItem(item.id)}
                        onMouseLeave={() => setHoveredItem(null)}
                      >
                        <div className="flex gap-4 p-4">
                          {/* 选择按钮 */}
                          <div className="flex-shrink-0 pt-8">
                            <button
                              onClick={() => !isOutOfStock && toggleSelectItem(item.id)}
                              className={`outline-none focus:outline-none transition-all ${
                                isOutOfStock ? 'opacity-30 cursor-not-allowed' : ''
                              }`}
                              disabled={isOutOfStock}
                            >
                              {selectedItems.has(item.id) ? (
                                <div className="flex items-center justify-center w-5-half h-5-half bg-gradient-to-br from-orange-500 to-red-500 text-white rounded shadow-sm">
                                  <CheckSquare className="w-3.5 h-3.5" />
                                </div>
                              ) : (
                                <div className={`w-5-half h-5-half border-2 rounded transition-colors ${
                                  hoveredItem === item.id && !isOutOfStock
                                    ? 'border-orange-400'
                                    : 'border-gray-300'
                                }`} />
                              )}
                            </button>
                          </div>

                          {/* 商品图片 */}
                          <div className="relative flex-shrink-0">
                            <div className={`w-24 h-24 rounded-lg overflow-hidden bg-gray-100 transition-all ${
                              hoveredItem === item.id ? 'shadow-lg scale-[1.02]' : 'shadow-sm'
                            }`}>
                              {item.product?.image_url ? (
                                <img
                                  src={item.product.image_url}
                                  alt={item.product.name}
                                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                                  onError={(e) => {
                                    e.target.src = `https://dummyimage.com/96x96/f5f5f5/999&text=${item.product?.name?.charAt(0) || '📦'}`;
                                  }}
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
                                  <Package className="w-10 h-10 text-gray-300" />
                                </div>
                              )}
                            </div>

                            {/* 库存标签 */}
                            {isOutOfStock && (
                              <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                                <span className="bg-gray-800 text-white text-xs px-3 py-1 rounded-full font-medium">
                                  已售罄
                                </span>
                              </div>
                            )}
                            {isLowStock && (
                              <div className="absolute top-1.5 left-1.5 bg-gradient-to-r from-orange-500 to-red-500 text-white text-xs px-2 py-0.5 rounded-full font-medium shadow-md">
                                仅剩{item.product.stock}件
                              </div>
                            )}

                            {/* 移除按钮 */}
                            {hoveredItem === item.id && !isOutOfStock && (
                              <button
                                onClick={() => removeItem(item.product_id)}
                                className="absolute -top-1.5 -right-1.5 bg-red-500 text-white p-1.5 rounded-full shadow-lg hover:scale-110 transition-all active:scale-95"
                                title="删除商品"
                              >
                                <Trash2 className="w-3 h-3" />
                              </button>
                            )}
                          </div>

                          {/* 商品信息 */}
                          <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                            <div>
                              {/* 商品标题 */}
                              <h3 className="font-medium text-gray-900 text-sm leading-snug line-clamp-2 mb-2 pr-2">
                                {item.product?.name || '未知商品'}
                              </h3>

                              {/* 商品属性 */}
                              <div className="flex flex-wrap items-center gap-1.5 mb-2">
                                {item.product?.category && (
                                  <span className="text-xs text-gray-500 bg-gray-50 px-2 py-0.5 rounded border border-gray-100">
                                    {item.product.category}
                                  </span>
                                )}
                                {item.product?.brand && (
                                  <span className="text-xs text-orange-600 bg-orange-50 px-2 py-0.5 rounded border border-orange-100">
                                    {item.product.brand}
                                  </span>
                                )}
                              </div>
                            </div>

                            <div className="flex items-end justify-between">
                              {/* 价格 */}
                              <div>
                                <div className="flex items-baseline gap-0.5">
                                  <span className="text-xs text-orange-500 font-bold">¥</span>
                                  <span className="text-xl font-bold text-orange-500">
                                    {(item.product?.price || 0).toFixed(2)}
                                  </span>
                                </div>
                                {item.product?.original_price && item.product.original_price > item.product.price && (
                                  <div className="flex items-center gap-2 mt-1">
                                    <span className="text-xs text-gray-400 line-through">
                                      ¥{item.product.original_price.toFixed(2)}
                                    </span>
                                    <span className="text-xs text-red-500 bg-red-50 px-1.5 py-0.5 rounded">
                                      省¥{(item.product.original_price - item.product.price).toFixed(2)}
                                    </span>
                                  </div>
                                )}
                              </div>

                              {/* 数量控制 */}
                              <div className={`flex items-center border rounded-lg overflow-hidden ${
                                isOutOfStock ? 'border-gray-200 opacity-50' : 'border-gray-200 shadow-sm'
                              }`}>
                                <button
                                  onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                                  className="w-8 h-8 flex items-center justify-center hover:bg-gray-50 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                                  disabled={item.quantity <= 1 || isEditingQuantity || isOutOfStock}
                                  title="减少"
                                >
                                  <Minus className="w-3.5 h-3.5 text-gray-600" />
                                </button>

                                <input
                                  type="number"
                                  min="1"
                                  max="99"
                                  value={editingQuantities[item.id] || item.quantity}
                                  onChange={(e) => handleQuantityInput(item.id, e.target.value)}
                                  onBlur={() => handleQuantityBlur(item.id)}
                                  className="w-12 h-8 text-center text-sm font-medium text-gray-900 border-0 outline-none bg-white disabled:bg-gray-50"
                                  disabled={isEditingQuantity || isOutOfStock}
                                />

                                <button
                                  onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                                  className="w-8 h-8 flex items-center justify-center hover:bg-gray-50 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                                  disabled={(item.product?.stock && item.quantity >= item.product.stock) || isEditingQuantity || isOutOfStock}
                                  title="增加"
                                >
                                  <Plus className="w-3.5 h-3.5 text-gray-600" />
                                </button>
                              </div>
                            </div>

                            {/* 小计和库存信息 */}
                            <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
                              <span className="text-xs text-gray-500">
                                小计: <span className="text-orange-500 font-bold">¥{((item.product?.price || 0) * item.quantity).toFixed(2)}</span>
                              </span>
                              <div className="flex items-center gap-3">
                                {item.product?.stock && item.product.stock > 0 && (
                                  <span className={`text-xs font-medium ${
                                    item.product.stock > 20 ? 'text-green-600' :
                                    item.product.stock > 10 ? 'text-blue-600' :
                                    'text-orange-600'
                                  }`}>
                                    {item.product.stock > 20 ? '库存充足' :
                                     item.product.stock > 10 ? `库存${item.product.stock}件` :
                                     `仅剩${item.product.stock}件`}
                                  </span>
                                )}
                                <button
                                  onClick={() => removeItem(item.product_id)}
                                  className="text-xs text-gray-400 hover:text-red-500 transition-colors flex items-center gap-1"
                                >
                                  <Trash2 className="w-3 h-3" />
                                  删除
                                </button>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 选中状态的光晕效果 */}
                        {selectedItems.has(item.id) && (
                          <div className="absolute inset-x-0 top-0 bottom-0 bg-gradient-to-r from-orange-100/20 via-orange-50/10 to-transparent pointer-events-none" />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 底部结算栏 */}
        {cart && cart.items.length > 0 && (
          <div className="sticky bottom-0 bg-white border-t border-gray-100 flex-shrink-0 shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
            <div className="p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-3">
                  <button
                    onClick={toggleSelectAll}
                    className="flex items-center gap-2.5 text-sm text-gray-700 hover:text-orange-500 transition-colors group"
                  >
                    {selectedItems.size === cart.items.length ? (
                      <div className="flex items-center justify-center w-5 h-5 bg-gradient-to-br from-orange-500 to-red-500 text-white rounded shadow-sm">
                        <CheckSquare className="w-3.5 h-3.5" />
                      </div>
                    ) : (
                      <div className="w-5 h-5 border-2 border-gray-300 rounded group-hover:border-orange-400 transition-colors" />
                    )}
                    <span className="font-medium">全选</span>
                  </button>

                  <div className="h-4 w-px bg-gray-200" />

                  <div className="text-sm text-gray-500">
                    已选 <span className="text-orange-500 font-bold">{selectedQuantity}</span> 件
                  </div>
                </div>

                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <div className="flex items-baseline justify-end gap-0.5">
                      <span className="text-sm text-gray-500 mr-1">合计：</span>
                      <span className="text-xs text-orange-500 font-bold">¥</span>
                      <span className="text-3xl font-bold text-orange-500">
                        {selectedPrice.toFixed(2)}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      不含运费
                    </div>
                  </div>

                  <button
                    className={`px-8 py-3.5 rounded-xl font-bold text-white transition-all duration-200 shadow-lg ${
                      selectedQuantity > 0
                        ? 'bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 hover:shadow-xl active:scale-95'
                        : 'bg-gradient-to-r from-gray-300 to-gray-400 cursor-not-allowed'
                    }`}
                    disabled={selectedQuantity === 0}
                  >
                    <div className="flex items-center gap-2">
                      <span>去结算</span>
                      {selectedQuantity > 0 && (
                        <span className="bg-white/20 px-2 py-0.5 rounded-full text-xs font-medium">
                          {selectedQuantity}
                        </span>
                      )}
                      <ChevronRight className="w-4 h-4" />
                    </div>
                  </button>
                </div>
              </div>

              {/* 优惠信息 */}
              {selectedPrice > 0 && (
                <div className="pt-3 border-t border-gray-100">
                  <div className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <Tag className="w-4 h-4 text-orange-500" />
                      <span className="text-gray-600">满99元包邮 · 满199减20 · 满299减50</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500">可省</span>
                      <span className="text-orange-500 font-bold text-lg">
                        ¥{(
                          selectedPrice >= 299 ? 50 :
                          selectedPrice >= 199 ? 20 :
                          selectedPrice >= 99 ? 0 : 0
                        ).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes cartFadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes cartSlideUp {
          from { transform: translateY(30px) scale(0.95); opacity: 0; }
          to { transform: translateY(0) scale(1); opacity: 1; }
        }
        .animate-fade-in {
          animation: cartFadeIn 0.25s ease-out;
        }
        .animate-slide-up {
          animation: cartSlideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .line-clamp-2 {
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
          -webkit-appearance: none;
          margin: 0;
        }
        .w-5-half {
          width: 1.375rem;
        }
        .h-5-half {
          height: 1.375rem;
        }
      `}</style>
    </div>
  );
};

export default CartModal;