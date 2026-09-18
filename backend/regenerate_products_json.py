"""
从数据库重新生成 products.json 文件
确保使用正确的 UTF-8 编码（无 BOM）和正确的图片路径格式
"""
import json
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from app.database import engine, get_db
from app.db_models import Product


def regenerate_products_json():
    """从数据库重新生成 products.json 文件"""

    # 输出文件路径
    output_path = backend_dir / "app" / "knowledge_base" / "products.json"

    print("开始从数据库重新生成 products.json...")

    # 从数据库读取所有商品
    db = Session(engine)
    try:
        products = db.query(Product).all()
        print(f"从数据库读取到 {len(products)} 个商品")

        # 转换为列表格式
        products_list = []
        for product in products:
            # 确保 image_url 使用正确的格式
            image_url = product.image_url
            if image_url:
                # 如果是 SVG 路径，替换为 JPG
                if '.svg' in image_url:
                    image_url = image_url.replace('.svg', '.jpg')

                # 确保路径以 /assets/ 开头
                if not image_url.startswith('/assets/'):
                    image_url = f"/assets/{image_url.lstrip('/')}"

            # 处理 features 字段（可能是 JSON 字符串或已经是字典）
            features = None
            if product.features:
                try:
                    features = json.loads(product.features) if isinstance(product.features, str) else product.features
                except json.JSONDecodeError:
                    features = None

            product_data = {
                "id": product.product_id,
                "name": product.name,
                "category": product.category,
                "price": product.price,
                "description": product.description or "",
                "features": features or [],
                "inventory": product.inventory,
                "image_url": image_url
            }
            products_list.append(product_data)

        # 写入 JSON 文件，使用 UTF-8 编码（无 BOM）
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(products_list, f, ensure_ascii=False, indent=2)

        print(f"✓ 成功生成 {output_path}")
        print(f"✓ 包含 {len(products_list)} 个商品")

        # 验证文件
        with open(output_path, 'r', encoding='utf-8') as f:
            try:
                test_data = json.load(f)
                print(f"✓ JSON 格式验证通过")
                print(f"✓ 文件编码正确（无 BOM）")

                # 显示前 3 个商品信息
                print("\n前 3 个商品预览：")
                for i, p in enumerate(test_data[:3], 1):
                    print(f"  {i}. {p['name']} - {p['image_url']}")
            except json.JSONDecodeError as e:
                print(f"✗ JSON 格式验证失败: {e}")
                return False

        return True

    except Exception as e:
        print(f"✗ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = regenerate_products_json()
    sys.exit(0 if success else 1)
