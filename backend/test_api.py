"""
测试运行中的服务API
"""
import requests
import json

def test_running_service():
    """测试运行中的服务"""
    print("=" * 60)
    print("测试运行中的服务API...")
    print("=" * 60)

    base_url = "http://localhost:8000"

    # 测试查询
    test_queries = [
        "推荐一些手机",
        "我想买羽绒服",
        "大衣怎么样",
        "有什么护肤品"
    ]

    for query in test_queries:
        print(f"\n🔍 查询: {query}")
        print("-" * 60)

        try:
            response = requests.post(
                f"{base_url}/chat/query",
                json={
                    "query": query,
                    "session_id": "test_session"
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"✓ 请求成功")
                print(f"  意图: {data.get('intent')}")
                print(f"  置信度: {data.get('confidence', 0):.2f}")

                retrieved_docs = data.get('retrieved_docs', [])
                print(f"  检索到 {len(retrieved_docs)} 个文档")
                if retrieved_docs:
                    for i, doc in enumerate(retrieved_docs[:2], 1):
                        print(f"    {i}. [{doc.get('score', 0):.2f}] {doc.get('content', '')[:50]}...")

                suggested_products = data.get('suggested_products', [])
                print(f"  推荐商品 {len(suggested_products)} 个")
                if suggested_products:
                    for i, product in enumerate(suggested_products[:2], 1):
                        print(f"    {i}. {product.get('name')} - ¥{product.get('price')}")

                answer = data.get('answer', '')
                print(f"  回复: {answer[:80]}...")
            else:
                print(f"✗ 请求失败: {response.status_code}")
                print(f"  错误信息: {response.text}")

        except requests.exceptions.ConnectionError:
            print(f"✗ 无法连接到服务，请确保服务正在运行")
            break
        except Exception as e:
            print(f"✗ 请求异常: {e}")

    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_running_service()