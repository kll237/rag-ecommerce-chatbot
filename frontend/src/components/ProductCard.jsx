import React, { useState, useEffect } from 'react';
import { ShoppingBag, Heart, Check, Loader2, AlertCircle } from 'lucide-react';

function ProductCard({
  product,
  API_BASE_URL = 'http://localhost:8000',
  session_id = null,
  onAddToCart = null,
  isWishlistMode = false,
  onRemoveFromWishlist = null
}) {
  const [imageError, setImageError] = useState(false);
  const [isInCart, setIsInCart] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(false);
  const [addingToCart, setAddingToCart] = useState(false);
  const [togglingWishlist, setTogglingWishlist] = useState(false);

  // 验证商品数据完整性
  const isValidProduct = product && typeof product === 'object';
  const productId = product?.id;
  const isValidProductId = productId !== undefined && productId !== null && typeof productId === 'number';

  // 在控制台输出诊断信息
  React.useEffect(() => {
    if (isValidProduct) {
      console.log(`[ProductCard] 商品数据验证:`, {
        name: product.name,
        id: productId,
        id_type: typeof productId,
        product_id: product.product_id,
        product_id_type: typeof product.product_id,
        is_valid_id: isValidProductId,
        image_url: product.image_url
      });

      if (!isValidProductId) {
        console.error(`[ProductCard] ❌ 商品ID无效:`, {
          name: product.name,
          id: productId,
          type: typeof productId
        });
      }
    } else {
      console.error('[ProductCard] ❌ 商品数据无效:', product);
    }
  }, [product, productId, isValidProductId]);

  // 检查商品是否在收藏中
  useEffect(() => {
    if (!isValidProductId) {
      console.warn('[ProductCard] 跳过收藏状态检查：商品ID无效');
      return;
    }

    const checkWishlistStatus = async () => {
      try {
        console.log(`[ProductCard] 检查收藏状态: product.id=${productId}`);
        const response = await fetch(`${API_BASE_URL}/wishlist/check/${productId}?user_id=1`);
        if (response.ok) {
          const data = await response.json();
          console.log(`[ProductCard] 收藏状态:`, data);
          setIsInWishlist(data.is_in_wishlist);
        } else {
          console.error(`[ProductCard] 检查收藏状态失败: HTTP ${response.status}`);
        }
      } catch (err) {
        console.error('[ProductCard] 检查收藏状态失败:', err);
      }
    };

    checkWishlistStatus();
  }, [productId, API_BASE_URL, isValidProductId]);

  // 加入购物车
  const handleAddToCart = async () => {
    if (!isValidProductId) {
      alert('⚠️ 商品数据不完整，无法添加到购物车。\n\n请确保后端数据库已初始化。\n运行命令: python init_all.py');
      return;
    }

    if (addingToCart || product.inventory <= 0) return;

    try {
      setAddingToCart(true);
      console.log(`[ProductCard] 添加到购物车: product.id=${productId}`);

      const url = session_id
        ? `${API_BASE_URL}/cart/items?user_id=1&session_id=${session_id}`
        : `${API_BASE_URL}/cart/items?user_id=1`;

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          product_id: productId,
          quantity: 1
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[ProductCard] 加入购物车失败:', response.status, errorText);
        throw new Error(`加入购物车失败 (HTTP ${response.status})`);
      }

      console.log('[ProductCard] 加入购物车成功');
      setIsInCart(true);
      setTimeout(() => setIsInCart(false), 2000);

      if (onAddToCart) {
        onAddToCart();
      }
    } catch (err) {
      console.error('[ProductCard] 加入购物车失败:', err);
      alert(`加入购物车失败: ${err.message}\n\n请检查后端服务是否正常运行。`);
    } finally {
      setAddingToCart(false);
    }
  };

  // 切换收藏状态
  const handleToggleWishlist = async (e) => {
    e.stopPropagation();

    if (!isValidProductId) {
      alert('⚠️ 商品数据不完整，无法添加收藏。\n\n请确保后端数据库已初始化。\n运行命令: python init_all.py');
      return;
    }

    if (togglingWishlist) return;

    try {
      setTogglingWishlist(true);

      if (isInWishlist) {
        // 取消收藏
        console.log(`[ProductCard] 取消收藏: product.id=${productId}`);
        const response = await fetch(`${API_BASE_URL}/wishlist/${productId}?user_id=1`, {
          method: 'DELETE',
        });
        if (!response.ok) throw new Error('取消收藏失败');
        console.log('[ProductCard] 取消收藏成功');
        setIsInWishlist(false);

        if (onRemoveFromWishlist) {
          onRemoveFromWishlist();
        }
      } else {
        // 添加收藏
        const url = session_id
          ? `${API_BASE_URL}/wishlist/${productId}?user_id=1&session_id=${session_id}`
          : `${API_BASE_URL}/wishlist/${productId}?user_id=1`;

        console.log(`[ProductCard] 添加收藏: product.id=${productId}`);
        const response = await fetch(url, {
          method: 'POST',
        });
        if (!response.ok) throw new Error('收藏失败');
        console.log('[ProductCard] 添加收藏成功');
        setIsInWishlist(true);
      }
    } catch (err) {
      console.error('[ProductCard] 收藏操作失败:', err);
      alert(`操作失败: ${err.message}\n\n请检查后端服务是否正常运行。`);
    } finally {
      setTogglingWishlist(false);
    }
  };

  if (!isValidProduct) {
    return (
      <div className="product-card bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div className="flex items-center gap-3 text-red-500">
          <AlertCircle className="w-6 h-6" />
          <div>
            <p className="font-semibold">商品数据无效</p>
            <p className="text-sm text-gray-500">请检查后端数据格式</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="product-card bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-all duration-300 hover:border-blue-300 relative">
      {/* 数据不完整警告 */}
      {!isValidProductId && (
        <div className="absolute inset-0 z-20 bg-red-50/95 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="text-center">
            <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-3" />
            <p className="font-semibold text-red-700 mb-2">商品数据不完整</p>
            <p className="text-sm text-red-600 mb-3">缺少有效的商品ID</p>
            <p className="text-xs text-gray-600">
              请运行: <code className="bg-gray-200 px-1 py-0.5 rounded">python init_all.py</code>
            </p>
          </div>
        </div>
      )}

      {/* 商品图片容器 - 关键优化：删除占位符背景，使用 object-contain 完整显示图片 */}
      <div className="relative h-36 bg-gray-50 flex items-center justify-center overflow-hidden">
        {imageError ? (
          <div className="text-4xl text-gray-300">📦</div>
        ) : (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-contain"
            onError={() => setImageError(true)}
          />
        )}

        {/* 库存标签 */}
        {product.inventory > 0 && product.inventory <= 10 && (
          <div className="absolute top-2 left-2 bg-orange-500 text-white text-xs px-2 py-1 rounded">
            仅剩 {product.inventory} 件
          </div>
        )}

        {/* 无库存标签 */}
        {product.inventory === 0 && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
            <span className="text-white font-semibold">暂时缺货</span>
          </div>
        )}
      </div>

      {/* 商品信息 */}
      <div className="p-3">
        <div className="mb-2">
          <span className="text-xs text-gray-500">{product.category}</span>
          <h3 className="text-sm font-semibold text-gray-900 line-clamp-1">{product.name}</h3>
        </div>

        <p className="text-xs text-gray-500 line-clamp-2 mb-2">{product.description}</p>

        <div className="flex items-center justify-between">
          <span className="text-base font-bold text-red-600">¥{product.price?.toFixed(2)}</span>

          {/* 操作按钮 */}
          <div className="flex gap-1">
            {!isWishlistMode && (
              <button
                onClick={handleAddToCart}
                disabled={product.inventory === 0 || addingToCart}
                className={`p-1.5 rounded-lg transition-all ${
                  isInCart
                    ? 'bg-green-500 text-white'
                    : product.inventory === 0
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                }`}
                title={isInCart ? '已加入购物车' : '加入购物车'}
              >
                {addingToCart ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : isInCart ? (
                  <Check className="w-4 h-4" />
                ) : (
                  <ShoppingBag className="w-4 h-4" />
                )}
              </button>
            )}

            <button
              onClick={handleToggleWishlist}
              disabled={togglingWishlist}
              className={`p-1.5 rounded-lg transition-all ${
                isInWishlist
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-50 text-gray-400 hover:bg-red-50 hover:text-red-500'
              }`}
              title={isInWishlist ? '取消收藏' : '添加收藏'}
            >
              {togglingWishlist ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : isInWishlist ? (
                <Heart className="w-4 h-4 fill-current" />
              ) : (
                <Heart className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductCard;