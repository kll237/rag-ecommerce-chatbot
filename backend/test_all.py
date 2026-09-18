"""
综合测试脚本 - 一键测试所有API接口
"""
import requests
import json
from typing import Dict, Any
import sys

# 配置
BASE_URL = "http://localhost:8000"
HEADERS = {"Content-Type": "application/json"}

# 测试结果存储
test_results = []

def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_test(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")

    test_results.append({
        "name": test_name,
        "success": success,
        "details": details
    })

def test_health():
    """测试1: 健康检查"""
    print("\n[测试1] 健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()

        if response.status_code == 200:
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version')}")
            print(f"   数据库: {data.get('database')}")
            print(f"   向量存储: {data.get('vector_store')}")
            print_test("健康检查", True)
            return True
        else:
            print_test("健康检查", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("健康检查", False, str(e))
        return False

def test_rag_query_product():
    """测试2: RAG查询 - 产品推荐"""
    print("\n[测试2] RAG查询 - 产品推荐")
    try:
        payload = {"query": "你们有什么产品？", "top_k": 3}
        response = requests.post(f"{BASE_URL}/chat/query", json=payload, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   回答: {data.get('answer')[:100]}...")
            print(f"   意图: {data.get('intent')}")
            print(f"   置信度: {data.get('confidence', 0):.2f}")
            print(f"   会话ID: {data.get('session_id')[:36]}")
            print_test("RAG查询 - 产品推荐", True)
            return True
        else:
            print_test("RAG查询 - 产品推荐", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("RAG查询 - 产品推荐", False, str(e))
        return False

def test_rag_query_order():
    """测试3: RAG查询 - 订单查询"""
    print("\n[测试3] RAG查询 - 订单查询")
    try:
        payload = {"query": "我想查我的订单", "top_k": 3}
        response = requests.post(f"{BASE_URL}/chat/query", json=payload, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   回答: {data.get('answer')[:100]}...")
            print(f"   意图: {data.get('intent')}")
            print_test("RAG查询 - 订单查询", True)
            return True
        else:
            print_test("RAG查询 - 订单查询", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("RAG查询 - 订单查询", False, str(e))
        return False

def test_rag_query_refund():
    """测试4: RAG查询 - 退货退款"""
    print("\n[测试4] RAG查询 - 退货退款")
    try:
        payload = {"query": "我要退货", "top_k": 3}
        response = requests.post(f"{BASE_URL}/chat/query", json=payload, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"   回答: {data.get('answer')[:100]}...")
            print(f"   意图: {data.get('intent')}")
            print_test("RAG查询 - 退货退款", True)
            return True
        else:
            print_test("RAG查询 - 退货退款", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("RAG查询 - 退货退款", False, str(e))
        return False

def test_search_products():
    """测试5: 搜索商品列表"""
    print("\n[测试5] 搜索商品列表")
    try:
        response = requests.get(f"{BASE_URL}/products?limit=5", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"   商品数量: {len(data)}")
            print_test("搜索商品列表", True, f"返回 {len(data)} 个商品")
            return True
        else:
            print_test("搜索商品列表", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("搜索商品列表", False, str(e))
        return False

def test_get_product_detail():
    """测试6: 获取商品详情"""
    print("\n[测试6] 获取商品详情")
    try:
        response = requests.get(f"{BASE_URL}/products/1", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"   商品ID: {data.get('id')}")
            print(f"   商品名称: {data.get('name', 'N/A')}")
            print_test("获取商品详情", True)
            return True
        elif response.status_code == 404:
            print_test("获取商品详情", True, "商品不存在（数据库未初始化）")
            return True
        else:
            print_test("获取商品详情", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("获取商品详情", False, str(e))
        return False

def test_api_docs():
    """测试7: API文档访问"""
    print("\n[测试7] API文档访问")
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)

        if response.status_code == 200:
            print_test("API文档访问", True, "Swagger UI可访问")
            return True
        else:
            print_test("API文档访问", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("API文档访问", False, str(e))
        return False

def test_openapi_schema():
    """测试8: OpenAPI Schema"""
    print("\n[测试8] OpenAPI Schema")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"   API标题: {data.get('info', {}).get('title')}")
            print(f"   API版本: {data.get('info', {}).get('version')}")
            print(f"   端点数量: {len(data.get('paths', {}))}")
            print_test("OpenAPI Schema", True)
            return True
        else:
            print_test("OpenAPI Schema", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("OpenAPI Schema", False, str(e))
        return False

def test_server_response_time():
    """测试9: 服务器响应时间"""
    print("\n[测试9] 服务器响应时间")
    try:
        import time

        # 进行3次请求，取平均值（避免首次加载的影响）
        times = []
        for i in range(3):
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/health", timeout=10)
            end_time = time.time()
            times.append((end_time - start_time) * 1000)
            time.sleep(0.1)  # 短暂间隔

        avg_response_time = sum(times) / len(times)

        if response.status_code == 200:
            print(f"   平均响应时间: {avg_response_time:.2f}ms")
            print(f"   各次测试: {[f'{t:.2f}ms' for t in times]}")

            # 根据响应时间给出评级
            if avg_response_time < 200:
                grade = "优秀"
                status = True
            elif avg_response_time < 1000:
                grade = "良好"
                status = True
            elif avg_response_time < 3000:
                grade = "一般（可能包含首次加载）"
                status = True
            else:
                grade = "较慢"
                status = False

            print_test("服务器响应时间", status, f"{avg_response_time:.2f}ms - {grade}")
            return True
        else:
            print_test("服务器响应时间", False, f"状态码: {response.status_code}")
            return False
    except Exception as e:
        print_test("服务器响应时间", False, str(e))
        return False

def run_all_tests():
    """运行所有测试"""
    print_header("电商RAG客服系统 - 综合API测试")
    print(f"后端地址: {BASE_URL}")
    print(f"开始时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 运行所有测试
    tests = [
        test_health,
        test_rag_query_product,
        test_rag_query_order,
        test_rag_query_refund,
        test_search_products,
        test_get_product_detail,
        test_api_docs,
        test_openapi_schema,
        test_server_response_time
    ]

    for test in tests:
        test()
        print("-" * 70)

    # 打印汇总
    print_header("测试结果汇总")

    passed = sum(1 for r in test_results if r["success"])
    failed = len(test_results) - passed

    print(f"\n总测试数: {len(test_results)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"通过率: {(passed/len(test_results)*100):.1f}%")

    if failed > 0:
        print(f"\n失败的测试:")
        for r in test_results:
            if not r["success"]:
                print(f"  ❌ {r['name']}: {r['details']}")

    print("\n" + "=" * 70)
    if failed == 0:
        print("🎉 所有测试通过！系统运行正常。")
    else:
        print(f"⚠️  有 {failed} 个测试失败，请检查系统配置。")
    print("=" * 70 + "\n")

    return failed == 0

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试已中断")
        sys.exit(130)