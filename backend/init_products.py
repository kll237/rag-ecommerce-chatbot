"""
初始化商品数据
从 products.json 导入商品到数据库
"""
import sys
import os
from pathlib import Path
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.db_models import Product
from app.config import config

def init_products():
    """初始化商品数据"""
    # 创建数据库会话
    db = SessionLocal()

    try:
        # 读取商品数据文件
        products_file = config.KNOWLEDGE_BASE_DIR / "products.json"
        if not products_file.exists():
            print(f"商品数据文件不存在: {products_file}")
            return

        with open(products_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)

        # 检查是否已有商品数据
        existing_products = db.query(Product).count()
        if existing_products > 0:
            print(f"数据库中已有 {existing_products} 个商品，清空后重新导入")
            # 删除所有现有商品
            db.query(Product).delete()
            db.commit()

        # 插入商品数据
        product_count = 0
        for product_data in products_data:
            product = Product(
                product_id=product_data['id'],
                name=product_data['name'],
                category=product_data.get('category', ''),
                price=product_data.get('price', 0),
                description=product_data.get('description', ''),
                inventory=product_data.get('inventory', 0),
                image_url=product_data.get('image_url', ''),
                features=json.dumps([], ensure_ascii=False)
            )
            db.add(product)
            product_count += 1

        # 提交更改
        db.commit()
        print(f"成功导入 {product_count} 个商品")

    except Exception as e:
        db.rollback()
        print(f"导入商品数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    init_products()
