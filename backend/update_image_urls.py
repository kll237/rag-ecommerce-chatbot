#!/usr/bin/env python3
"""
批量更新 products.json 中的 image_url
将 dummyimage.com 占位符替换为本地路径
"""
import json
import re

# 读取原始文件
input_file = "app/knowledge_base/products.json"
output_file = "app/knowledge_base/products.json"

with open(input_file, 'r', encoding='utf-8') as f:
    products = json.load(f)

# 更新每个商品的 image_url
for product in products:
    product_id = product['id']
    # 提取数字部分（p001 -> 001）
    num = product_id[1:]  # 去掉 'p'
    # 设置新的本地路径
    product['image_url'] = f"/assets/{product_id}.jpg"
    print(f"✅ 更新 {product_id}: {product['name']} -> /assets/{product_id}.jpg")

# 写回文件
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(products, f, ensure_ascii=False, indent=2)

print(f"\n✨ 完成！共更新 {len(products)} 个商品的图片路径")