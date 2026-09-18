import React from 'react';

function ProductDetailModal({ product, features, onClose }) {
  // 解析商品描述
  const description = product.description || '暂无商品描述';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content product-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>商品详情</h2>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="product-detail-body">
          <div className="product-detail-image">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                onError={(e) => {
                  e.target.style.display = 'none';
                  e.target.parentElement.innerHTML = '<div class="placeholder-image-large">📦</div>';
                }}
              />
            ) : (
              <div className="placeholder-image-large">📦</div>
            )}
          </div>

          <div className="product-detail-info">
            <h3 className="product-detail-name">{product.name}</h3>

            <div className="product-detail-meta">
              {product.category && (
                <div className="product-detail-category">
                  <span className="label">类别:</span>
                  <span className="value">{product.category}</span>
                </div>
              )}

              {product.price && (
                <div className="product-detail-price">
                  <span className="label">价格:</span>
                  <span className="value price-highlight">¥{product.price.toFixed(2)}</span>
                </div>
              )}

              {product.inventory !== undefined && (
                <div className="product-detail-inventory">
                  <span className="label">库存:</span>
                  <span className={`value ${product.inventory > 0 ? 'in-stock' : 'out-of-stock'}`}>
                    {product.inventory > 0 ? `${product.inventory}件` : '缺货'}
                  </span>
                </div>
              )}
            </div>

            <div className="product-detail-description">
              <h4>商品描述</h4>
              <p>{description}</p>
            </div>

            {features && features.length > 0 && (
              <div className="product-detail-features">
                <h4>商品特性</h4>
                <ul>
                  {features.map((feature, index) => (
                    <li key={index}>{feature}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="product-detail-actions">
              {product.inventory > 0 ? (
                <button className="add-to-cart-btn">加入购物车</button>
              ) : (
                <button className="add-to-cart-btn" disabled>暂时缺货</button>
              )}
              <button className="consult-btn">咨询客服</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProductDetailModal;