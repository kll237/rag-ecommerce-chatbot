"""
RAG引擎核心实现
"""
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .config import config
from .vector_store import get_vector_store
from .ai_models.classifier import IntentClassifier
from .ai_models.embedder import EmbeddingModel
from .ai_models.generator import ResponseGenerator
from .ai_models.reranker import Reranker

class RAGEngine:
    """RAG引擎"""

    def __init__(self):
        self.vector_store = get_vector_store()
        self.classifier = IntentClassifier()
        self.embedder = EmbeddingModel()
        self.generator = ResponseGenerator()
        self.reranker = Reranker()
        self.is_initialized = False

    def initialize(self):
        """初始化RAG引擎"""
        if self.is_initialized:
            return

        # 先尝试从磁盘加载向量数据库
        vector_db_path = Path(config.VECTOR_DB_PATH)
        vector_db_file = vector_db_path / "vector_store.pkl"

        if vector_db_file.exists():
            try:
                self.vector_store.load(config.VECTOR_DB_PATH)
                # 检查加载的文档数
                doc_count = len(self.vector_store.documents)
                if doc_count > 0:
                    print(f"从磁盘加载向量数据库: {config.VECTOR_DB_PATH}")
                    print(f"加载了 {doc_count} 个文档")
                    self.is_initialized = True
                    print("RAG引擎初始化完成")
                    return
                else:
                    print(f"向量数据库为空（0个文档），将重新加载知识库")
            except Exception as e:
                print(f"加载向量数据库失败: {e}，将重新加载知识库")

        # 加载知识库
        self._load_knowledge_base()

        # 保存向量数据库到磁盘
        try:
            self.save_knowledge_base()
        except Exception as e:
            print(f"保存向量数据库失败: {e}")

        self.is_initialized = True
        print("RAG引擎初始化完成")

    def _load_knowledge_base(self):
        """加载知识库到向量存储"""
        # 加载FAQ
        faq_path = config.KNOWLEDGE_BASE_DIR / "faq.txt"
        if faq_path.exists():
            print(f"加载 FAQ 知识库...")
            with open(faq_path, 'r', encoding='utf-8-sig') as f:
                faq_content = f.read()

            # 解析FAQ（格式：Q: 问题 A: 答案）
            faqs = self._parse_faq(faq_content)
            print(f"解析了 {len(faqs)} 个 FAQ")

            # 添加到向量存储
            documents = []
            metadatas = []
            for qa in faqs:
                documents.append(qa['question'] + " " + qa['answer'])
                metadatas.append({
                    'type': 'faq',
                    'question': qa['question'],
                    'answer': qa['answer']
                })

            if documents:
                self.vector_store.add_documents(documents, metadatas)
                print(f"成功添加 {len(documents)} 个 FAQ 文档到向量存储")
        else:
            print(f"警告：FAQ 文件不存在: {faq_path}")

        # 加载商品信息
        products_path = config.KNOWLEDGE_BASE_DIR / "products.json"
        if products_path.exists():
            print(f"加载商品知识库...")
            with open(products_path, 'r', encoding='utf-8-sig') as f:
                products = json.load(f)
            print(f"读取了 {len(products)} 个商品")

            documents = []
            metadatas = []
            for product in products:
                doc = f"{product['name']} {product.get('category', '')} {product.get('description', '')}"
                documents.append(doc)
                metadatas.append({
                    'type': 'product',
                    'product_id': product['id'],
                    'name': product['name'],
                    'price': product.get('price', 0),
                    'category': product.get('category'),
                    'description': product.get('description'),
                    'inventory': product.get('inventory', 0),
                    'image_url': product.get('image_url')
                })

            if documents:
                self.vector_store.add_documents(documents, metadatas)
                print(f"成功添加 {len(documents)} 个商品文档到向量存储")
        else:
            print(f"警告：商品文件不存在: {products_path}")

        print(f"知识库加载完成，共 {len(self.vector_store.documents)} 个文档")

    def _parse_faq(self, content: str) -> List[Dict]:
        """解析FAQ文本"""
        faqs = []
        lines = content.split('\n')
        current_qa = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_qa:
                    faqs.append(current_qa)
                current_qa = {'question': line[2:].strip(), 'answer': ''}
            elif line.startswith('A:'):
                current_qa['answer'] = line[2:].strip()

        if current_qa:
            faqs.append(current_qa)

        return faqs

    def query(
        self,
        user_query: str,
        session_id: str = None,
        top_k: int = 5,
        db = None
    ) -> Dict[str, Any]:
        """
        处理用户查询

        Args:
            user_query: 用户查询
            session_id: 会话ID
            top_k: 检索文档数量
            db: 数据库会话（可选，用于查询完整商品信息）

        Returns:
            包含答案、意图、检索文档等信息的字典
        """
        # 1. 意图识别
        intent, confidence = self.classifier.classify(user_query)

        # 2. 检索相关文档
        # 如果是商品查询，增加检索数量以确保能获取到商品信息
        search_top_k = top_k * 3 if intent == 'product_inquiry' else top_k
        retrieved_docs = self.vector_store.search(user_query, top_k=search_top_k)

        # 3. 如果是商品查询，优先保留商品类型的文档
        if intent == 'product_inquiry':
            product_docs = [doc for doc in retrieved_docs if doc.get('metadata', {}).get('type') == 'product']
            faq_docs = [doc for doc in retrieved_docs if doc.get('metadata', {}).get('type') != 'product']
            # 优先使用商品文档，如果不够则补充FAQ文档
            retrieved_docs = product_docs[:top_k] if len(product_docs) >= top_k else product_docs + faq_docs[:top_k - len(product_docs)]

        # 4. 重排序
        if len(retrieved_docs) > config.TOP_K_RERANK:
            retrieved_docs = self.reranker.rerank(user_query, retrieved_docs, top_k=config.TOP_K_RERANK)

        # 5. 生成响应
        context = [doc['content'] for doc in retrieved_docs]
        answer = self.generator.generate(user_query, context, intent)

        # 6. 提取相关商品
        suggested_products = self._extract_products(retrieved_docs, db)

        return {
            'answer': answer,
            'intent': intent,
            'confidence': confidence,
            'retrieved_docs': retrieved_docs,
            'suggested_products': suggested_products,
            'session_id': session_id
        }

    def _extract_products(self, retrieved_docs: List[Dict], db = None) -> List[Dict]:
        """从检索结果中提取商品"""
        products = []
        from .crud import get_product_by_product_id

        for doc in retrieved_docs:
            metadata = doc.get('metadata', {})
            if metadata.get('type') == 'product':
                product_id_str = metadata.get('product_id')

                # 如果有数据库会话，查询完整商品信息
                if db and product_id_str:
                    product = get_product_by_product_id(db, product_id_str)
                    if product:
                        products.append({
                            'id': product.id,  # 数据库主键（整数）
                            'product_id': product.product_id,  # 商品ID（字符串）
                            'name': product.name,
                            'category': product.category,
                            'price': product.price,
                            'description': product.description,
                            'features': product.features,
                            'inventory': product.inventory,
                            'image_url': product.image_url
                        })
                else:
                    # 回退到使用metadata中的完整信息
                    products.append({
                        'product_id': metadata.get('product_id'),
                        'name': metadata.get('name'),
                        'category': metadata.get('category'),
                        'price': metadata.get('price'),
                        'description': metadata.get('description'),
                        'inventory': metadata.get('inventory', 0),
                        'image_url': metadata.get('image_url')
                    })

        return products[:3]  # 最多返回3个商品

    def add_document(self, document: str, metadata: Dict = None):
        """添加单个文档到知识库"""
        self.vector_store.add_documents([document], [metadata] if metadata else None)

    def add_documents(self, documents: List[str], metadatas: List[Dict] = None):
        """批量添加文档"""
        self.vector_store.add_documents(documents, metadatas)

    def save_knowledge_base(self):
        """保存知识库"""
        self.vector_store.save(config.VECTOR_DB_PATH)
        print(f"知识库已保存到 {config.VECTOR_DB_PATH}")

    def load_knowledge_base(self):
        """加载知识库"""
        vector_db_path = Path(config.VECTOR_DB_PATH)
        if vector_db_path.exists():
            self.vector_store.load(config.VECTOR_DB_PATH)
            print(f"知识库已从 {config.VECTOR_DB_PATH} 加载")

# 全局RAG引擎实例
rag_engine = RAGEngine()
