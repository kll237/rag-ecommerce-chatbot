"""
重新创建向量数据库
解决向量数据库加载失败的问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path
import shutil

print("="*80)
print("重新创建向量数据库")
print("="*80)

# 1. 删除旧的向量数据库
print("\n1. 删除旧向量数据库...")
vector_db_path = Path("app/data/vector_store")

if vector_db_path.exists():
    shutil.rmtree(vector_db_path)
    print("   ✅ 已删除旧向量数据库")
else:
    print("   ⚠️ 向量数据库不存在")

# 2. 初始化新的RAG引擎
print("\n2. 初始化RAG引擎...")
from app.rag_engine import RAGEngine

rag = RAGEngine()
rag.initialize()

print(f"   ✅ RAG引擎初始化完成")
print(f"   文档总数: {len(rag.vector_store.documents)}")
print(f"   索引类型: {type(rag.vector_store.index).__name__}")

# 3. 验证向量数据库
print("\n3. 验证向量数据库...")

# 检查文件
if vector_db_path.exists():
    files = list(vector_db_path.glob("*"))
    print(f"   向量数据库文件数: {len(files)}")
    for f in files:
        size = f.stat().st_size / 1024
        print(f"   - {f.name} ({size:.2f} KB)")

# 测试搜索
print("\n4. 测试向量搜索...")
test_query = "推荐几款手机"
result = rag.query(test_query, "test", top_k=5)

print(f"   查询: {test_query}")
print(f"   意图: {result.get('intent')}")
print(f"   检索文档数: {len(result.get('retrieved_docs', []))}")
print(f"   推荐商品数: {len(result.get('suggested_products', []))}")

if len(result.get('retrieved_docs', [])) > 0:
    print("\n   ✅ 向量搜索成功！")
    print("\n   检索结果:")
    for i, doc in enumerate(result.get('retrieved_docs', [])[:3], 1):
        metadata = doc.get('metadata', {})
        print(f"   {i}. Type={metadata.get('type')}, Score={doc.get('score', 0):.4f}")
        if metadata.get('type') == 'product':
            print(f"      商品: {metadata.get('name')} - ¥{metadata.get('price')}")
else:
    print("   ❌ 向量搜索失败，没有返回结果")

print("\n" + "="*80)
print("向量数据库重建完成！")
print("="*80)
print("\n请重启后端服务:")
print("  1. 按 Ctrl+C 停止当前服务")
print("  2. 运行: .\\start.ps1")
