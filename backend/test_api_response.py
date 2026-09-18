"""
测试API响应，查看返回的字段
"""
import requests
import json

API_BASE = "http://localhost:8000"

print("="*80)
print("测试API响应字段")
print("="*80)

test_query = "推荐几款手机"

print(f"\n查询: {test_query}")
print("-"*80)

response = requests.post(
    f"{API_BASE}/chat/query",
    params={"user_id": 1, "session_id": "test_api"},
    json={"query": test_query},
    timeout=10
)

if response.status_code == 200:
    data = response.json()
    print(f"\n✅ API响应成功")
    print(f"\n完整响应:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print(f"\n字段列表:")
    for key in data.keys():
        print(f"  - {key}: {type(data[key]).__name__}")
        if key == 'suggested_products':
            print(f"    值: {data[key]}")
else:
    print(f"\n❌ API响应失败: {response.status_code}")
    print(f"   {response.text}")
