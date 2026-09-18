"""
快速诊断脚本 - 检查为什么商品推荐没有返回结果
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def check_database():
    """检查数据库商品数量"""
    print("="*80)
    print("1. 检查数据库商品数据")
    print("="*80)

    try:
        from app.database import SessionLocal
        from app.crud import get_all_products

        db = SessionLocal()
        try:
            products = get_all_products(db, limit=200)
            print(f"✅ 数据库商品总数: {len(products)}")

            if len(products) > 0:
                print("\n商品分类统计:")
                categories = {}
                for p in products:
                    cat = p.category or "未知"
                    categories[cat] = categories.get(cat, 0) + 1
                for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                    print(f"  - {cat}: {count}个")
            else:
                print("❌ 数据库中没有商品数据！")
        finally:
            db.close()
    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        import traceback
        traceback.print_exc()

def check_vector_store():
    """检查向量存储状态"""
    print("\n" + "="*80)
    print("2. 检查向量存储")
    print("="*80)

    try:
        from app.rag_engine import RAGEngine
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            print("初始化RAG引擎...")
            rag = RAGEngine()
            rag.initialize()

            # 检查向量存储
            print(f"✅ 向量存储类型: {type(rag.vector_store).__name__}")
            print(f"✅ 嵌入器类型: {type(rag.embedder).__name__}")
            print(f"✅ 检索器类型: {type(rag.retriever).__name__}")

            # 检查文档数量
            if hasattr(rag.vector_store, 'document_count'):
                print(f"✅ 文档总数: {rag.vector_store.document_count}")
            if hasattr(rag.vector_store, 'documents'):
                print(f"✅ 文档列表长度: {len(rag.vector_store.documents)}")

            # 测试查询
            print("\n测试查询: 推荐几款手机")
            result = rag.query("推荐几款手机", "test_session", top_k=5, db=db)

            print(f"  - 意图: {result.get('intent')}")
            print(f"  - 置信度: {result.get('confidence', 0):.2%}")
            print(f"  - 检索文档数: {len(result.get('retrieved_docs', []))}")
            print(f"  - 推荐商品数: {len(result.get('suggested_products', []))}")

            # 分析检索的文档
            retrieved_docs = result.get('retrieved_docs', [])
            if retrieved_docs:
                print("\n检索到的文档:")
                for i, doc in enumerate(retrieved_docs[:3], 1):
                    metadata = doc.get('metadata', {})
                    doc_type = metadata.get('type', 'unknown')
                    score = doc.get('score', 0)
                    content = doc.get('content', '')[:50]
                    print(f"  {i}. [{doc_type}] (score={score:.3f}) {content}...")
            else:
                print("⚠️ 没有检索到任何文档！")

            # 分析推荐商品
            suggested = result.get('suggested_products', [])
            if suggested:
                print("\n推荐的商品:")
                for i, prod in enumerate(suggested[:3], 1):
                    print(f"  {i}. {prod.get('name')} - ¥{prod.get('price')}")
            else:
                print("⚠️ 没有推荐商品！")

        finally:
            db.close()

    except Exception as e:
        print(f"❌ 检查向量存储失败: {e}")
        import traceback
        traceback.print_exc()

def check_embedding_model():
    """检查嵌入模型配置"""
    print("\n" + "="*80)
    print("3. 检查嵌入模型配置")
    print("="*80)

    try:
        from app.config import config
        import os

        use_sentence = os.environ.get('USE_SENTENCE_TRANSFORMERS', '').lower()
        print(f"USE_SENTENCE_TRANSFORMERS环境变量: {use_sentence}")

        if hasattr(config, 'EMBEDDING_MODEL'):
            print(f"配置中的嵌入模型: {config.EMBEDDING_MODEL}")

        # 检查向量数据库文件
        vector_db_path = "app/data/vector_store"
        if os.path.exists(vector_db_path):
            files = os.listdir(vector_db_path)
            print(f"\n向量数据库文件:")
            for f in files:
                file_path = os.path.join(vector_db_path, f)
                size = os.path.getsize(file_path) / 1024
                print(f"  - {f} ({size:.2f} KB)")
        else:
            print("❌ 向量数据库目录不存在")

    except Exception as e:
        print(f"❌ 检查配置失败: {e}")

if __name__ == "__main__":
    print("\n🔍 商品推荐功能快速诊断\n")
    check_database()
    check_vector_store()
    check_embedding_model()
    print("\n" + "="*80)
    print("诊断完成")
    print("="*80)
