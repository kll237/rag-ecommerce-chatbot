"""
配置文件
"""
import os
from pathlib import Path
from typing import Optional

# 加载.env文件
try:
    from dotenv import load_dotenv
    # 加载.env文件（从backend目录）
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # 如果没有安装dotenv，忽略

class Config:
    # 基础路径
    BASE_DIR = Path(__file__).parent.parent
    APP_DIR = BASE_DIR / "app"
    DATA_DIR = APP_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    KNOWLEDGE_BASE_DIR = APP_DIR / "knowledge_base"
    MODELS_DIR = APP_DIR / "models"
    TRAINING_DIR = APP_DIR / "train"

    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ecommerce_rag.db"
    )

    # 向量数据库配置
    VECTOR_DB_TYPE: str = os.getenv("VECTOR_DB_TYPE", "faiss")
    VECTOR_DB_PATH: str = str(DATA_DIR / "vector_store")
    EMBEDDING_DIM: int = 768

    # 大模型配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")

    # 百度翻译配置
    BAIDU_TRANSLATE_APP_ID: Optional[str] = os.getenv("BAIDU_TRANSLATE_APP_ID", "")
    BAIDU_TRANSLATE_SECRET_KEY: Optional[str] = os.getenv("BAIDU_TRANSLATE_SECRET_KEY", "")

    # 豆包大模型配置
    DOUBAO_API_KEY: Optional[str] = os.getenv("DOUBAO_API_KEY", "your-doubao-api-key")
    DOUBAO_BASE_URL: str = os.getenv("DOUBAO_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
    DOUBAO_MODEL: str = os.getenv("DOUBAO_MODEL", "doubao-seed-1-6-vision-250815")
    # 语音识别专用模型（可选）
    DOUBAO_ASR_MODEL: str = os.getenv("DOUBAO_ASR_MODEL", DOUBAO_MODEL)
    # 图片识别专用模型（可选）
    DOUBAO_VISION_MODEL: str = os.getenv("DOUBAO_VISION_MODEL", DOUBAO_MODEL)

    # 本地模型配置
    LOCAL_EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    LOCAL_LLM_MODEL: Optional[str] = None

    # RAG配置
    TOP_K_RETRIEVAL: int = 5
    TOP_K_RERANK: int = 3
    CHUNK_SIZE: int = 256
    CHUNK_OVERLAP: int = 50
    SIMILARITY_THRESHOLD: float = 0.1  # 降低阈值以支持简化的嵌入方法

    # 训练配置
    BATCH_SIZE: int = 32
    LEARNING_RATE: float = 2e-5
    EPOCHS: int = 3
    MAX_LENGTH: int = 512

    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5176",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5176"
    ]

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @classmethod
    def init_directories(cls):
        """初始化必要的目录"""
        for dir_path in [
            cls.RAW_DATA_DIR,
            cls.PROCESSED_DATA_DIR,
            cls.KNOWLEDGE_BASE_DIR,
            cls.MODELS_DIR,
            cls.TRAINING_DIR,
            cls.DATA_DIR / "vector_store",
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)

config = Config()
config.init_directories()