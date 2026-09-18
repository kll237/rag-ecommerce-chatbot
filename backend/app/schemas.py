"""
Pydantic schemas定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# ============= 用户相关 =============
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# ============= 聊天会话相关 =============
class ChatSessionBase(BaseModel):
    title: Optional[str] = None

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    id: int
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ============= 聊天消息相关 =============
class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: Optional[int] = None

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    role: str
    intent: Optional[str]
    confidence: Optional[float]
    retrieved_docs: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# ============= RAG响应相关 =============
class RetrievedDoc(BaseModel):
    content: str
    score: float
    metadata: Optional[dict] = None

class RAGRequest(BaseModel):
    query: str = Field(..., description="用户查询")
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    top_k: Optional[int] = Field(5, description="检索文档数量")

class RAGResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    retrieved_docs: List[RetrievedDoc]
    suggested_products: Optional[List[dict]] = None
    session_id: str
    message_id: Optional[int] = None  # 新增：助手消息ID，用于反馈

# ============= 商品相关 =============
class ProductBase(BaseModel):
    name: str
    category: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class Product(ProductBase):
    id: int
    product_id: str
    features: Optional[str]
    inventory: int
    image_url: Optional[str]

    class Config:
        from_attributes = True

# ============= 反馈相关 =============
class FeedbackCreate(BaseModel):
    message_id: int
    rating: int
    comment: Optional[str] = None
    is_helpful: Optional[bool] = None

# ============= 翻译相关 =============
class TranslateRequest(BaseModel):
    text: str = Field(..., description="需要翻译的文本")
    target_language: str = Field(..., description="目标语言: en, ja, ko, fr, es, de")

class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    target_language: str

# ============= 语音识别相关 =============
class VoiceRecognizeRequest(BaseModel):
    audio_data: str = Field(..., description="音频数据（base64编码）")
    audio_format: str = Field("mp3", description="音频格式: mp3, wav, pcm, ogg")

class VoiceRecognizeResponse(BaseModel):
    text: str = Field(..., description="识别的文字内容")
    duration: Optional[float] = Field(None, description="音频时长（秒）")

# ============= 图片识别相关 =============
class ImageRecognizeRequest(BaseModel):
    image_data: str = Field(..., description="图片数据（base64编码）")
    question: Optional[str] = Field("请识别这张图片中的商品，提供商品名称、类别和简要描述", description="询问问题")

class ImageRecognizeResponse(BaseModel):
    description: str = Field(..., description="商品描述")
    product_name: Optional[str] = Field(None, description="商品名称")
    category: Optional[str] = Field(None, description="商品类别")
    features: Optional[List[str]] = Field(None, description="商品特征")
    suggested_price: Optional[str] = Field(None, description="建议价格范围")

# ============= 语音合成相关 =============
class TextToSpeechRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000, description="要合成的文本")
    speaker: Optional[str] = Field("zh_female_xiaohe_uranus_bigtts", description="音色ID")
    audio_format: Optional[str] = Field("mp3", description="音频格式: mp3, pcm, ogg_opus")
    sample_rate: Optional[int] = Field(24000, description="采样率: 8000, 16000, 22050, 24000, 32000, 44100, 48000")
    speech_rate: Optional[int] = Field(0, ge=-50, le=100, description="语速调整: -50到100")
    loudness_rate: Optional[int] = Field(0, ge=-50, le=100, description="音量调整: -50到100")

class TextToSpeechResponse(BaseModel):
    audio_data: str = Field(..., description="音频数据（base64编码）")
    audio_size: int = Field(..., description="音频大小（字节）")
    format: str = Field(..., description="音频格式")
    sample_rate: int = Field(..., description="采样率")
    speaker: str = Field(..., description="使用的音色")
    method: str = Field(..., description="合成方法: tts/demo")

class SpeakerInfo(BaseModel):
    id: str
    name: str
    category: str

class SpeakersResponse(BaseModel):
    speakers: List[SpeakerInfo]


# ============= 健康检查 =============
class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    vector_store: str

# ============= 购物车相关 =============
class CartItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: int
    product_id: int
    quantity: int
    product: Optional[Product] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    id: int
    user_id: int
    session_id: Optional[str]
    items: List[CartItemResponse]
    total_quantity: int
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class CartAddRequest(BaseModel):
    product_id: int
    quantity: int = 1

class CartUpdateRequest(BaseModel):
    product_id: int
    quantity: int

class CartClearRequest(BaseModel):
    pass

# ============= 商品收藏相关 =============
class WishlistItem(BaseModel):
    id: int
    user_id: int
    product_id: int
    product: Product
    session_id: Optional[str] = None
    created_at: datetime

class WishlistResponse(BaseModel):
    items: List[WishlistItem]
    total_count: int

# ============= 导出历史相关 =============
class ExportHistoryRequest(BaseModel):
    session_ids: List[int] = []

# ============= 批量删除会话相关 =============
class DeleteSessionsRequest(BaseModel):
    session_ids: List[int]

# ============= 数据分析相关 =============
class SessionStatistics(BaseModel):
    """会话统计数据"""
    total_sessions: int = Field(..., description="总会话数")
    today_sessions: int = Field(..., description="今日会话数")
    total_messages: int = Field(..., description="总消息数")
    avg_messages_per_session: float = Field(..., description="平均每会话消息数")
    total_users: int = Field(..., description="总用户数")

class UserBehaviorStatistics(BaseModel):
    """用户行为统计数据"""
    total_cart_operations: int = Field(..., description="购物车操作次数")
    total_wishlist_operations: int = Field(..., description="收藏操作次数")
    total_product_views: int = Field(..., description="商品查看次数")
    total_feedbacks: int = Field(..., description="反馈提交次数")

class ProductRankingItem(BaseModel):
    """热门商品排行项"""
    product_id: int = Field(..., description="商品ID")
    name: str = Field(..., description="商品名称")
    category: Optional[str] = Field(None, description="商品类别")
    price: Optional[float] = Field(None, description="商品价格")
    popularity_score: int = Field(..., description="热度值(购物车+收藏次数)")
    cart_count: int = Field(..., description="购物车中出现次数")
    wishlist_count: int = Field(..., description="收藏次数")

class IntentDistributionItem(BaseModel):
    """意图分布项"""
    intent: str = Field(..., description="意图类型")
    count: int = Field(..., description="出现次数")
    percentage: float = Field(..., description="占比")

class AnalyticsReport(BaseModel):
    """综合分析报告"""
    session_stats: SessionStatistics = Field(..., description="会话统计")
    user_behavior: UserBehaviorStatistics = Field(..., description="用户行为统计")
    top_products: List[ProductRankingItem] = Field(..., description="热门商品排行")
    intent_distribution: List[IntentDistributionItem] = Field(..., description="意图分布")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")