"""
购物车和商品推荐功能测试脚本
在Windows本地PyCharm中运行
"""
import requests
import json
from typing import Dict, List, Any

# API基础URL - 确保后端服务已启动
API_BASE = "http://localhost:8000"

def print_section(title: str):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(operation: str, success: bool, data: Any = None):
    """打印测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    print(f"\n[{status}] {operation}")
    if data:
        print(json.dumps(data, ensure_ascii=False, indent=2))

# ==================== 购物车功能测试 ====================

def test_get_cart(user_id: int = 1, session_id: str = "test_session"):
    """测试获取购物车"""
    try:
        response = requests.get(
            f"{API_BASE}/cart",
            params={"user_id": user_id, "session_id": session_id}
        )
        data = response.json()
        print_result("获取购物车", response.status_code == 200, data)
        return data
    except Exception as e:
        print_result("获取购物车", False, str(e))
        return None

def test_add_to_cart(product_id: int, quantity: int = 1, user_id: int = 1, session_id: str = "test_session"):
    """测试添加商品到购物车"""
    try:
        response = requests.post(
            f"{API_BASE}/cart/items",
            params={"user_id": user_id, "session_id": session_id},
            json={"product_id": product_id, "quantity": quantity}
        )
        data = response.json()
        print_result(f"添加商品ID {product_id} 到购物车 (数量: {quantity})", response.status_code == 200, data)
        return data
    except Exception as e:
        print_result(f"添加商品ID {product_id} 到购物车", False, str(e))
        return None

def test_update_cart_item(product_id: int, quantity: int, user_id: int = 1, session_id: str = "test_session"):
    """测试更新购物车商品数量"""
    try:
        response = requests.put(
            f"{API_BASE}/cart/items/{product_id}",
            params={"user_id": user_id, "session_id": session_id},
            json={"quantity": quantity}
        )
        data = response.json()
        print_result(f"更新商品ID {product_id} 数量为 {quantity}", response.status_code == 200, data)
        return data
    except Exception as e:
        print_result(f"更新商品ID {product_id} 数量", False, str(e))
        return None

def test_remove_from_cart(product_id: int, user_id: int = 1, session_id: str = "test_session"):
    """测试从购物车移除商品"""
    try:
        response = requests.delete(
            f"{API_BASE}/cart/items/{product_id}",
            params={"user_id": user_id, "session_id": session_id}
        )
        data = response.json()
        print_result(f"从购物车移除商品ID {product_id}", response.status_code == 200, data)
        return data
    except Exception as e:
        print_result(f"从购物车移除商品ID {product_id}", False, str(e))
        return None

def test_clear_cart(user_id: int = 1, session_id: str = "test_session"):
    """测试清空购物车"""
    try:
        response = requests.delete(
            f"{API_BASE}/cart",
            params={"user_id": user_id, "session_id": session_id}
        )
        data = response.json()
        print_result("清空购物车", response.status_code == 200, data)
        return data
    except Exception as e:
        print_result("清空购物车", False, str(e))
        return None

# ==================== 商品推荐功能测试 ====================

def test_product_recommendation(query: str, user_id: int = 1, session_id: str = "test_session"):
    """测试商品推荐"""
    try:
        response = requests.post(
            f"{API_BASE}/chat/query",
            params={"user_id": user_id, "session_id": session_id},
            json={"query": query}
        )
        data = response.json()

        # 提取推荐商品
        recommended_products = data.get("suggested_products", [])

        print_result(f"商品推荐 - 查询: '{query}'", response.status_code == 200, {
            "query": query,
            "response": data.get("answer", ""),
            "intent": data.get("intent", ""),
            "confidence": data.get("confidence", 0),
            "recommended_products_count": len(recommended_products),
            "recommended_products": recommended_products
        })

        return data
    except Exception as e:
        print_result(f"商品推荐 - 查询: '{query}'", False, str(e))
        return None

# ==================== 主测试流程 ====================

def run_cart_tests():
    """运行购物车功能测试"""
    print_section("购物车功能测试")

    session_id = "test_session_001"

    # 1. 获取初始购物车
    print("\n[1/6] 获取初始购物车")
    cart = test_get_cart(user_id=1, session_id=session_id)

    # 2. 清空购物车（确保测试环境干净）
    print("\n[2/6] 清空购物车")
    test_clear_cart(user_id=1, session_id=session_id)

    # 3. 添加商品到购物车
    print("\n[3/6] 添加多个商品到购物车")
    test_add_to_cart(product_id=1, quantity=2, user_id=1, session_id=session_id)  # iPhone 15 Pro Max
    test_add_to_cart(product_id=11, quantity=1, user_id=1, session_id=session_id)  # MacBook Pro
    test_add_to_cart(product_id=21, quantity=3, user_id=1, session_id=session_id)  # Sony耳机

    # 4. 查看购物车
    print("\n[4/6] 查看购物车")
    cart = test_get_cart(user_id=1, session_id=session_id)
    if cart:
        print(f"\n  📊 购物车统计:")
        print(f"    - 商品总数: {cart.get('total_quantity', 0)}")
        print(f"    - 总金额: ¥{cart.get('total_price', 0):,.2f}")
        print(f"    - 商品种类: {len(cart.get('items', []))}")
        print(f"\n  📦 商品详情:")
        for i, item in enumerate(cart.get('items', []), 1):
            product = item.get('product', {})
            print(f"    {i}. {product.get('name', '未知')} x{item.get('quantity', 0)} = ¥{product.get('price', 0) * item.get('quantity', 0)}")

    # 5. 更新商品数量
    print("\n[5/6] 更新商品数量 (将iPhone数量改为1)")
    test_update_cart_item(product_id=1, quantity=1, user_id=1, session_id=session_id)

    # 6. 移除商品
    print("\n[6/6] 移除商品 (移除Sony耳机)")
    test_remove_from_cart(product_id=21, user_id=1, session_id=session_id)

    # 7. 再次查看购物车
    print("\n[最终] 查看更新后的购物车")
    cart = test_get_cart(user_id=1, session_id=session_id)
    if cart:
        print(f"\n  📊 更新后统计:")
        print(f"    - 商品总数: {cart.get('total_quantity', 0)}")
        print(f"    - 总金额: ¥{cart.get('total_price', 0):,.2f}")
        print(f"    - 商品种类: {len(cart.get('items', []))}")

def run_recommendation_tests():
    """运行商品推荐测试"""
    print_section("商品推荐功能测试")

    session_id = "test_session_002"

    test_queries = [
        "推荐几款手机",
        "我想买一件大衣",
        "有什么好的笔记本电脑推荐吗",
        "推荐一些家电产品",
        "给我推荐一些数码产品"
    ]

    print("\n📝 测试查询列表:")
    for i, query in enumerate(test_queries, 1):
        print(f"  {i}. {query}")

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"  [{i}/{len(test_queries)}] 测试查询: {query}")
        print(f"{'='*80}")
        result = test_product_recommendation(query, user_id=1, session_id=session_id)

        if result:
            # 分析推荐结果
            recommended = result.get("recommended_products", [])
            intent = result.get("intent", "")
            confidence = result.get("confidence", 0)

            print(f"\n  📊 分析结果:")
            print(f"    - 意图识别: {intent}")
            print(f"    - 置信度: {confidence:.2%}")

            if recommended:
                print(f"    - 推荐商品数: {len(recommended)}")
                print(f"\n  🛍️ 推荐的商品:")
                for j, product in enumerate(recommended[:3], 1):
                    print(f"    {j}. {product.get('name', '未知')} - ¥{product.get('price', 0)}")
                    print(f"       类别: {product.get('category', '未知')}")
            else:
                print(f"\n  ⚠️ 未推荐商品")

def run_comprehensive_test():
    """运行完整测试"""
    print_section("购物车和商品推荐功能完整测试")
    print(f"  后端服务地址: {API_BASE}")
    print(f"  测试时间: {json.dumps({'timestamp': 'N/A'}, ensure_ascii=False)}")

    # 测试购物车功能
    run_cart_tests()

    # 测试商品推荐功能
    run_recommendation_tests()

    print_section("测试完成")
    print("  ✅ 所有测试已执行完成")
    print("  📝 请查看上方测试结果")
    print("  💡 如果发现异常，请检查:")
    print("     1. 后端服务是否正常运行 (http://localhost:8000)")
    print("     2. 数据库是否有商品数据")
    print("     3. 向量数据库是否已初始化")

def main():
    """主函数"""
    try:
        # 检查后端服务是否可用
        print("\n🔍 检查后端服务...")
        try:
            response = requests.get(f"{API_BASE}/docs", timeout=5)
            if response.status_code == 200:
                print(f"✅ 后端服务正常运行 ({API_BASE})")
            else:
                print(f"⚠️ 后端服务响应异常，状态码: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ 无法连接到后端服务 ({API_BASE})")
            print("💡 请确保后端服务已启动: 在backend目录下运行 start.ps1 或 start.bat")
            return
        except Exception as e:
            print(f"❌ 检查后端服务时出错: {e}")
            return

        # 运行完整测试
        run_comprehensive_test()

    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
