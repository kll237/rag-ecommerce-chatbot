#!/usr/bin/env python3
"""
批量更新数据库中的商品图片URL
"""
from app.database import SessionLocal
from app.db_models import Product

db = SessionLocal()

# 获取所有商品
products = db.query(Product).all()
print(f"找到 {len(products)} 个商品")

# 更新每个商品的 image_url
for product in products:
    new_image_url = f"/assets/{product.product_id}.jpg"
    if product.image_url != new_image_url:
        print(f"更新 {product.product_id}: {product.name} -> {new_image_url}")
        product.image_url = new_image_url

db.commit()
db.close()

print(f"\n✨ 完成！已更新所有商品的图片路径")