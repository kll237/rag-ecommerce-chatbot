"""
直接测试API响应
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_query():
    """测试单个查询"""
    query = "推荐几款手机"

    print("=" * 80)
    print(f"测试查询: {query}")
    print("=" * 80)

    try:
        response = requests.post(
            f"{API_BASE}/chat/query",
            json={
                "query": query,
                "session_id": "test_debug",
                "user_id": 1,
                "top_k": 3
            },
            timeout=30
        )

        print(f"\n状态码: {response.status_code}")
        print(f"\n完整响应（JSON）:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))

        # 检查关键字段
        data = response.json()
        print(f"\n\n关键字段检查:")
        print(f"  - answer: '{data.get('answer', '')}'")
        print(f"  - answer长度: {len(data.get('answer', ''))}")
        print(f"  - intent: {data.get('intent')}")
        print(f"  - confidence: {data.get('confidence')}")
        print(f"  - retrieved_docs数量: {len(data.get('retrieved_docs', []))}")
        print(f"  - suggested_products数量: {len(data.get('suggested_products', []))}")

        if data.get('retrieved_docs'):
            print(f"\n  检索到的文档:")
            for i, doc in enumerate(data.get('retrieved_docs', []), 1):
                print(f"    {i}. {doc.get('content', '')[:100]}... (score: {doc.get('score', 0)})")

        if data.get('suggested_products'):
            print(f"\n  推荐的商品:")
            for i, prod in enumerate(data.get('suggested_products', []), 1):
                print(f"    {i}. {prod.get('name')} - ¥{prod.get('price')}")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_query()
