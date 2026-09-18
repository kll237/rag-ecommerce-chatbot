"""
测试商品数据是否正确
运行此脚本验证数据库中的商品数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.db_models import Product
from app.rag_engine import rag_engine

def test_database():
    """测试数据库商品数据"""
    print("=" * 60)
    print("测试数据库商品数据")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 检查商品数量
        count = db.query(Product).count()
        print(f"\n✅ 数据库中的商品数量: {count}")

        if count == 0:
            print("\n❌ 数据库中没有商品数据！")
            print("请运行: python init_all.py")
            return False

        # 显示前5个商品
        print("\n前5个商品:")
        products = db.query(Product).limit(5).all()
        for i, p in enumerate(products, 1):
            print(f"\n  [{i}]")
            print(f"      数据库ID (id): {p.id} (类型: {type(p.id).__name__})")
            print(f"      商品ID (product_id): {p.product_id} (类型: {type(p.product_id).__name__})")
            print(f"      名称: {p.name}")
            print(f"      图片URL: {p.image_url}")
            print(f"      价格: {p.price}")

        return True

    finally:
        db.close()

def test_rag_response():
    """测试RAG引擎返回的推荐商品数据格式"""
    print("\n" + "=" * 60)
    print("测试RAG引擎推荐商品数据格式")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 模拟查询"推荐手机"
        result = rag_engine.query(
            user_query="推荐手机",
            session_id=None,
            top_k=5,
            db=db
        )

        print(f"\n✅ 意图识别: {result['intent']} (置信度: {result['confidence']:.2f})")
        print(f"✅ 推荐商品数量: {len(result['suggested_products'])}")

        if result['suggested_products']:
            print("\n推荐商品数据格式:")
            for i, product in enumerate(result['suggested_products'], 1):
                print(f"\n  [{i}]")
                print(f"      数据库ID (id): {product.get('id')} (类型: {type(product.get('id')).__name__})")
                print(f"      商品ID (product_id): {product.get('product_id')} (类型: {type(product.get('product_id')).__name__})")
                print(f"      名称: {product.get('name')}")
                print(f"      图片URL: {product.get('image_url')}")
                print(f"      价格: {product.get('price')}")

                # 检查id字段是否存在且为数字
                if 'id' in product and isinstance(product['id'], int):
                    print(f"      ✅ id字段正确（整数）")
                else:
                    print(f"      ❌ id字段错误或缺失！")

        return True

    finally:
        db.close()

if __name__ == "__main__":
    print("\n开始测试...\n")

    # 测试数据库
    db_ok = test_database()

    # 测试RAG引擎
    if db_ok:
        test_rag_response()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
