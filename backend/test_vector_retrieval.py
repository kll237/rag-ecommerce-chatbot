"""
测试向量检索功能
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.rag_engine import rag_engine
from app.database import SessionLocal

print("="*80)
print("向量检索测试")
print("="*80)

db = SessionLocal()
try:
    # 测试查询
    result = rag_engine.query('推荐几款手机', 'test', top_k=5, db=db)

    print(f"\n查询: 推荐几款手机")
    print(f"意图: {result.get('intent')}")
    print(f"置信度: {result.get('confidence', 0):.2%}")
    print(f"检索文档数: {len(result.get('retrieved_docs', []))}")
    print(f"推荐商品数: {len(result.get('suggested_products', []))}")

    print("\n检索到的文档:")
    retrieved_docs = result.get('retrieved_docs', [])
    if retrieved_docs:
        for i, doc in enumerate(retrieved_docs[:5], 1):
            metadata = doc.get('metadata', {})
            score = doc.get('score', 0)
            doc_type = metadata.get('type', 'unknown')
            content = doc.get('content', '')[:100]

            print(f"\n{i}. Type={doc_type}, Score={score:.4f}")
            print(f"   Content: {content}...")

            if doc_type == 'product':
                print(f"   Product ID: {metadata.get('product_id')}")
                print(f"   Name: {metadata.get('name')}")
    else:
        print("  ❌ 没有检索到任何文档！")

    print("\n推荐的商品:")
    suggested = result.get('suggested_products', [])
    if suggested:
        for i, prod in enumerate(suggested[:3], 1):
            print(f"{i}. {prod.get('name')} - ¥{prod.get('price')}")
    else:
        print("  ❌ 没有推荐商品！")

finally:
    db.close()

print("\n" + "="*80)
