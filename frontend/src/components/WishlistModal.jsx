import { useState, useEffect } from 'react';
import { X, Heart, Trash2, ShoppingBag } from 'lucide-react';
import ProductCard from './ProductCard';

const WishlistModal = ({ isOpen, onClose, session_id, API_BASE_URL, onAddToCart }) => {
  const [wishlist, setWishlist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchWishlist = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/wishlist?user_id=1`);
      if (!response.ok) {
        throw new Error('获取收藏列表失败');
      }
      const data = await response.json();
      setWishlist(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const removeFromWishlist = async (productId) => {
    if (!confirm('确定要从收藏中移除该商品吗？')) return;

    try {
      const response = await fetch(`${API_BASE_URL}/wishlist/${productId}?user_id=1`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('移除失败');
      }
      await fetchWishlist();
    } catch (err) {
      alert(err.message);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchWishlist();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col">
        {/* 标题栏 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <Heart className="w-6 h-6 text-red-500 fill-red-500" />
            <h2 className="text-2xl font-bold text-gray-800">我的收藏</h2>
            {wishlist && (
              <span className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm font-medium">
                {wishlist.total_count} 件商品
              </span>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* 内容区 */}
        <div className="flex-1 overflow-y-auto p-6">
          {loading ? (
            <div className="flex items-center justify-center h-40 text-gray-500">
              加载中...
            </div>
          ) : error ? (
            <div className="text-center text-red-500 py-8">{error}</div>
          ) : !wishlist || wishlist.items.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Heart className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-lg">收藏夹是空的</p>
              <p className="text-sm mt-2">收藏喜欢的商品，方便下次查看</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {wishlist.items.map((item) => (
                <div key={item.id} className="relative group">
                  {/* 收藏删除按钮 */}
                  <button
                    onClick={() => removeFromWishlist(item.product_id)}
                    className="absolute top-2 right-2 z-10 w-8 h-8 bg-white rounded-full shadow-md flex items-center justify-center text-red-500 hover:bg-red-50 transition-all opacity-0 group-hover:opacity-100"
                    title="移除收藏"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  {/* 商品卡片 */}
                  <ProductCard
                    product={item.product}
                    API_BASE_URL={API_BASE_URL}
                    session_id={session_id}
                    onAddToCart={onAddToCart}
                    isWishlistMode={true}
                    onRemoveFromWishlist={() => removeFromWishlist(item.product_id)}
                  />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* 底部提示 */}
        {wishlist && wishlist.items.length > 0 && (
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
              <ShoppingBag className="w-4 h-4" />
              <span>提示：点击商品卡片上的按钮可直接添加到购物车</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default WishlistModal;