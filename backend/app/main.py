"""
FastAPI主程序
"""
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from contextlib import asynccontextmanager
import uuid
import hashlib
import random
import base64
import json  # 添加json模块导入

# 导入豆包API客户端
from .doubao_api import asr_client, vision_client, tts_client

from .config import config
from .database import get_db, init_db
from .schemas import (
    UserCreate, User, ChatSessionCreate, ChatSession,
    ChatMessageCreate, ChatMessage, RAGRequest, RAGResponse,
    Product, FeedbackCreate, HealthResponse,
    TranslateRequest, TranslateResponse,
    VoiceRecognizeRequest, VoiceRecognizeResponse,
    ImageRecognizeRequest, ImageRecognizeResponse,
    TextToSpeechRequest, TextToSpeechResponse, SpeakersResponse,
    CartAddRequest, CartUpdateRequest, CartResponse, WishlistResponse, WishlistItem, ExportHistoryRequest, DeleteSessionsRequest,
    SessionStatistics, UserBehaviorStatistics, ProductRankingItem, IntentDistributionItem, AnalyticsReport
)
from .crud import (
    create_user, get_user, get_user_by_username,
    create_chat_session, get_chat_sessions, get_chat_session_by_id,
    create_chat_message, get_chat_messages,
    delete_chat_session, delete_chat_sessions,
    search_products, get_product_by_id, create_feedback,
    get_or_create_cart, add_to_cart, remove_from_cart,
    update_cart_item_quantity, clear_cart, get_cart,
    add_to_wishlist, remove_from_wishlist, get_wishlist, is_product_in_wishlist,
    export_chat_history,
    get_session_statistics, get_user_behavior_statistics, get_top_products, get_intent_distribution, get_analytics_report
)
from .rag_engine import rag_engine

# 应用生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    print("初始化数据库...")
    init_db()

    print("初始化RAG引擎...")
    rag_engine.initialize()

    yield

    # 关闭时执行
    print("应用关闭")

# 创建FastAPI应用
app = FastAPI(
    title="电商RAG客服系统API",
    description="基于RAG的智能电商客服系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS（完整配置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
    max_age=3600,  # 预检请求缓存时间（秒）
)

# ============= 根路径 =============
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "电商RAG客服系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }

# ============= 健康检查 =============
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        database="connected",
        vector_store="ready"
    )

# ============= 用户相关 =============
@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(user: UserCreate, db = Depends(get_db)):
    """创建用户"""
    # 检查用户名是否已存在
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )

    return create_user(db, user)

@app.get("/users/{user_id}", response_model=User)
async def get_user_endpoint(user_id: int, db = Depends(get_db)):
    """获取用户信息"""
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

# ============= 聊天会话相关 =============
@app.post("/chat/sessions", response_model=ChatSession, status_code=status.HTTP_201_CREATED)
async def create_chat_session_endpoint(
    session: ChatSessionCreate,
    user_id: int = 1,
    db = Depends(get_db)
):
    """创建聊天会话"""
    return create_chat_session(db, user_id, session.title)

@app.get("/chat/sessions", response_model=list[ChatSession])
async def get_chat_sessions_endpoint(
    user_id: int = 1,
    db = Depends(get_db)
):
    """获取用户的所有会话"""
    return get_chat_sessions(db, user_id)

@app.get("/chat/sessions/{session_id}", response_model=ChatSession)
async def get_chat_session_endpoint(session_id: int, db = Depends(get_db)):
    """获取指定会话（通过数据库ID）"""
    session = get_chat_session_by_id(db, session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return session

# 批量删除路由必须在单条删除路由之前，避免路由冲突
@app.delete("/chat/sessions/batch")
async def delete_chat_sessions_endpoint(request: DeleteSessionsRequest, db = Depends(get_db)):
    """批量删除会话"""
    deleted_count = delete_chat_sessions(db, request.session_ids)
    return {"deleted_count": deleted_count}

@app.delete("/chat/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session_endpoint(session_id: int, db = Depends(get_db)):
    """删除指定会话"""
    success = delete_chat_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.get("/chat/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_chat_messages_endpoint(session_id: int, db = Depends(get_db)):
    """获取会话的所有消息（通过数据库ID）"""
    return get_chat_messages(db, session_id)

@app.get("/chat/session/by-uuid/{session_uuid}/messages", response_model=list[ChatMessage])
async def get_chat_messages_by_uuid_endpoint(session_uuid: str, db = Depends(get_db)):
    """获取会话的所有消息（通过session_id字符串UUID）"""
    from .db_models import ChatSession
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_uuid
    ).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    return get_chat_messages(db, session.id)

# ============= RAG查询 =============
@app.post("/chat/query", response_model=RAGResponse)
async def query_rag(request: RAGRequest, db = Depends(get_db)):
    """
    RAG查询接口

    处理用户查询，返回基于知识库的响应
    """
    try:
        # 调用RAG引擎
        result = rag_engine.query(
            user_query=request.query,
            session_id=request.session_id,
            top_k=request.top_k or config.TOP_K_RETRIEVAL,
            db=db  # 传递数据库会话以获取完整商品信息
        )

        # 如果提供了会话ID，保存消息到数据库
        assistant_message_id = None
        if request.session_id:
            from .db_models import ChatSession
            # 查找会话，如果不存在则自动创建
            session = db.query(ChatSession).filter(
                ChatSession.session_id == request.session_id
            ).first()

            # 如果会话不存在，创建新会话（使用前端传的 session_id）
            if not session:
                session = create_chat_session(db, user_id=1, title=None, session_id=request.session_id)

            # 保存用户消息
            create_chat_message(
                db, session.id, 'user', request.query,
                result['intent'], result['confidence']
            )

            # 保存助手消息
            assistant_msg = create_chat_message(
                db, session.id, 'assistant', result['answer'],
                result['intent'], result['confidence'],
                str(result['retrieved_docs'])
            )
            assistant_message_id = assistant_msg.id

        return RAGResponse(
            answer=result['answer'],
            intent=result['intent'],
            confidence=result['confidence'],
            retrieved_docs=result['retrieved_docs'],
            suggested_products=result['suggested_products'],
            session_id=request.session_id or str(uuid.uuid4()),
            message_id=assistant_message_id  # 返回助手消息ID
        )

    except Exception as e:
        print(f"查询错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"查询处理失败: {str(e)}"
        )


# ============= 商品相关 =============
@app.get("/products", response_model=list[Product])
async def search_products_endpoint(
    query: str = None,
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    limit: int = 10,
    db = Depends(get_db)
):
    """搜索商品"""
    return search_products(db, query, category, min_price, max_price, limit)

@app.get("/products/{product_id}", response_model=Product)
async def get_product_endpoint(product_id: int, db = Depends(get_db)):
    """获取商品详情"""
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )
    return product

# ============= 反馈相关 =============
@app.post("/feedback", status_code=status.HTTP_201_CREATED)
async def submit_feedback_endpoint(feedback: FeedbackCreate, db = Depends(get_db)):
    """提交用户反馈"""
    return create_feedback(db, feedback)

# ============= 翻译相关 =============
@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    """
    翻译文本

    支持多种语言翻译：英语、日语、韩语、法语、西班牙语、德语
    使用百度翻译 API
    """
    try:
        import httpx

        # 检查百度翻译配置
        if not config.BAIDU_TRANSLATE_APP_ID or not config.BAIDU_TRANSLATE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="百度翻译未配置，请在 .env 文件中设置 BAIDU_TRANSLATE_APP_ID 和 BAIDU_TRANSLATE_SECRET_KEY"
            )

        # 语言映射（百度翻译使用的语言代码）
        language_map = {
            'en': 'en',      # 英语
            'ja': 'jp',      # 日语（百度使用 jp）
            'ko': 'kor',     # 韩语（百度使用 kor）
            'fr': 'fra',     # 法语（百度使用 fra）
            'es': 'spa',     # 西班牙语（百度使用 spa）
            'de': 'de'       # 德语
        }

        # 检查目标语言是否支持
        if request.target_language not in language_map:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"不支持的目标语言: {request.target_language}。支持的语言: {', '.join(language_map.keys())}"
            )

        # 百度翻译 API 参数
        app_id = config.BAIDU_TRANSLATE_APP_ID
        secret_key = config.BAIDU_TRANSLATE_SECRET_KEY
        salt = str(random.randint(32768, 65536))
        sign_str = app_id + request.text + salt + secret_key
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        # 请求参数
        params = {
            'q': request.text,
            'from': 'auto',
            'to': language_map[request.target_language],
            'appid': app_id,
            'salt': salt,
            'sign': sign
        }

        # 调用百度翻译 API
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                'https://fanyi-api.baidu.com/api/trans/vip/translate',
                params=params
            )

            if response.status_code != 200:
                error_detail = response.text
                print(f"百度翻译 API 错误: {error_detail}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"翻译服务调用失败: {error_detail}"
                )

            result = response.json()

            # 检查 API 返回的错误
            if 'error_code' in result:
                error_codes = {
                    '52001': '请求超时',
                    '52002': '系统错误',
                    '52003': '未授权用户',
                    '54000': '必填参数为空',
                    '54001': '签名错误',
                    '54003': '访问频率受限',
                    '54004': '账户余额不足',
                    '58000': '客户端IP非法',
                    '58001': '语言不支持',
                    '58002': '服务当前已不可用'
                }
                error_msg = error_codes.get(result['error_code'], f'未知错误({result["error_code"]})')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"百度翻译 API 错误: {error_msg}"
                )

            # 提取翻译结果
            if 'trans_result' not in result or not result['trans_result']:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="翻译结果为空"
                )

            # 百度翻译返回的是数组，合并所有翻译段落
            translated_text = ' '.join([item['dst'] for item in result['trans_result']])

        return TranslateResponse(
            original_text=request.text,
            translated_text=translated_text,
            target_language=request.target_language
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"翻译错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"翻译失败: {str(e)}"
        )


# ============= 语音识别相关 =============
@app.post("/voice/recognize", response_model=VoiceRecognizeResponse)
async def recognize_voice(request: VoiceRecognizeRequest):
    """
    语音识别（语音转文字）

    使用豆包语音识别服务将音频转换为文字
    支持格式：MP3, WAV, PCM, OGG
    """
    try:
        # 生成用户ID（如果没有提供）
        user_id = str(uuid.uuid4())

        # 调用豆包语音识别API
        result = await asr_client.recognize(
            audio_data=request.audio_data,
            uid=user_id
        )

        print(f"语音识别成功: {result['text']}")

        return VoiceRecognizeResponse(
            text=result['text'],
            duration=result.get('duration')
        )

    except Exception as e:
        print(f"语音识别错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}"
        )


# ============= 图片识别相关 =============
@app.post("/image/recognize", response_model=ImageRecognizeResponse)
async def recognize_image(request: ImageRecognizeRequest):
    """
    图片识别（识别商品）

    使用豆包多模态大模型识别图片中的商品
    可以识别商品名称、类别、特征等信息
    """
    try:
        # 调用豆包多模态大模型API进行图片识别
        result_text = await vision_client.recognize_image(
            image_data=request.image_data,
            question=request.question or "请识别这张图片中的商品"
        )

        print(f"图片识别成功: {result_text}")

        # 解析识别结果
        product_name = ""
        category = ""
        description = ""
        features = []
        suggested_price = ""

        # 按行解析结果
        lines = result_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('商品名称：') or line.startswith('商品名称:'):
                product_name = line.split('：')[-1].split(':')[-1].strip()
            elif line.startswith('类别：') or line.startswith('类别:'):
                category = line.split('：')[-1].split(':')[-1].strip()
            elif line.startswith('描述：') or line.startswith('描述:'):
                description = line.split('：')[-1].split(':')[-1].strip()
            elif line.startswith('特征：') or line.startswith('特征:'):
                features_str = line.split('：')[-1].split(':')[-1].strip()
                features = [f.strip() for f in features_str.split('、') if f.strip()]
            elif line.startswith('建议价格：') or line.startswith('建议价格:'):
                suggested_price = line.split('：')[-1].split(':')[-1].strip()

        # 如果解析失败，使用原始文本作为描述
        if not product_name and not category:
            description = result_text

        return ImageRecognizeResponse(
            description=description or result_text,
            product_name=product_name or "未知商品",
            category=category or "其他",
            features=features if features else ["暂无特征信息"],
            suggested_price=suggested_price or "价格未知"
        )

    except Exception as e:
        print(f"图片识别错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片识别失败: {str(e)}"
        )


# ============= 语音合成（TTS）相关 =============
@app.post("/chat/tts", response_model=TextToSpeechResponse)
async def text_to_speech(request: TextToSpeechRequest):
    """
    文本转语音（TTS）

    将文本转换为语音音频

    Args:
        request: TTS请求参数

    Returns:
        音频数据（base64编码）
    """
    try:
        print(f"[TTS] 收到语音合成请求，文本长度: {len(request.text)}")

        # 调用TTS客户端
        result = await tts_client.synthesize(
            text=request.text,
            uid="default",
            speaker=request.speaker,
            audio_format=request.audio_format,
            sample_rate=request.sample_rate,
            speech_rate=request.speech_rate,
            loudness_rate=request.loudness_rate
        )

        # 将音频数据转换为base64
        audio_base64 = base64.b64encode(result["audio_data"]).decode("utf-8")

        print(f"[TTS] 语音合成成功，音频大小: {result['audio_size']} bytes")

        return TextToSpeechResponse(
            audio_data=audio_base64,
            audio_size=result["audio_size"],
            format=result["format"],
            sample_rate=result["sample_rate"],
            speaker=result["speaker"],
            method=result["method"]
        )

    except Exception as e:
        print(f"[TTS] 语音合成错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}"
        )


@app.get("/chat/tts/speakers", response_model=SpeakersResponse)
async def get_tts_speakers():
    """
    获取可用的音色列表

    Returns:
        音色列表
    """
    try:
        speakers_dict = tts_client.get_available_speakers()

        # 转换为标准格式
        speakers = []
        for speaker_id, description in speakers_dict.items():
            # 解析音色类别
            category = "通用"
            if "有声书" in description or "朗读" in description:
                category = "有声书"
            elif "视频" in description or "配音" in description:
                category = "视频配音"
            elif "角色" in description or "扮演" in description:
                category = "角色扮演"
            elif "男声" in description:
                category = "男声"
            elif "女声" in description:
                category = "女声"

            speakers.append({
                "id": speaker_id,
                "name": description.split("（")[0].strip(),
                "category": category
            })

        return SpeakersResponse(speakers=speakers)

    except Exception as e:
        print(f"获取音色列表错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取音色列表失败: {str(e)}"
        )


@app.post("/chat/tts/stream")
async def text_to_speech_stream(request: TextToSpeechRequest):
    """
    文本转语音（流式返回音频）

    将文本转换为语音音频，直接返回音频流（非base64）

    Args:
        request: TTS请求参数

    Returns:
        音频流
    """
    try:
        print(f"[TTS Stream] 收到流式语音合成请求，文本长度: {len(request.text)}")

        # 调用TTS客户端
        result = await tts_client.synthesize(
            text=request.text,
            uid="default",
            speaker=request.speaker,
            audio_format=request.audio_format,
            sample_rate=request.sample_rate,
            speech_rate=request.speech_rate,
            loudness_rate=request.loudness_rate
        )

        print(f"[TTS Stream] 语音合成成功，音频大小: {result['audio_size']} bytes")

        # 根据音频格式返回正确的Content-Type
        content_type_map = {
            "mp3": "audio/mpeg",
            "pcm": "audio/pcm",
            "ogg_opus": "audio/opus"
        }

        content_type = content_type_map.get(result["format"], "audio/mpeg")

        return Response(
            content=result["audio_data"],
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=tts_output.{result['format']}",
                "X-Audio-Size": str(result["audio_size"]),
                "X-Audio-Format": result["format"],
                "X-Sample-Rate": str(result["sample_rate"]),
                "X-Speaker": result["speaker"]
            }
        )

    except Exception as e:
        print(f"[TTS Stream] 流式语音合成错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"流式语音合成失败: {str(e)}"
        )


# ============= 购物车相关 =============
@app.get("/cart", response_model=CartResponse)
async def get_cart_endpoint(
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """获取购物车"""
    cart = get_cart(db, user_id, session_id)
    if not cart:
        # 创建空购物车
        cart = get_or_create_cart(db, user_id, session_id)

    # 计算总数量和总价
    total_quantity = sum(item.quantity for item in cart.items)
    total_price = sum(
        (item.product.price or 0) * item.quantity
        for item in cart.items if item.product
    )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": item.product
            }
            for item in cart.items
        ],
        total_quantity=total_quantity,
        total_price=round(total_price, 2),
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

@app.post("/cart/items", response_model=CartResponse)
async def add_to_cart_endpoint(
    request: CartAddRequest,
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """添加商品到购物车"""
    # 验证商品是否存在
    product = get_product_by_id(db, request.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    cart = add_to_cart(db, user_id, request.product_id, request.quantity, session_id)

    # 计算总数量和总价
    total_quantity = sum(item.quantity for item in cart.items)
    total_price = sum(
        (item.product.price or 0) * item.quantity
        for item in cart.items if item.product
    )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": item.product
            }
            for item in cart.items
        ],
        total_quantity=total_quantity,
        total_price=round(total_price, 2),
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

@app.delete("/cart/items/{product_id}", response_model=CartResponse)
async def remove_from_cart_endpoint(
    product_id: int,
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """从购物车移除商品"""
    cart = remove_from_cart(db, user_id, product_id, session_id)

    # 计算总数量和总价
    total_quantity = sum(item.quantity for item in cart.items)
    total_price = sum(
        (item.product.price or 0) * item.quantity
        for item in cart.items if item.product
    )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": item.product
            }
            for item in cart.items
        ],
        total_quantity=total_quantity,
        total_price=round(total_price, 2),
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

@app.put("/cart/items/{product_id}", response_model=CartResponse)
async def update_cart_item_endpoint(
    product_id: int,
    request: CartUpdateRequest,
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """更新购物车商品数量"""
    quantity = request.quantity

    if quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="数量不能为负数"
        )

    cart = update_cart_item_quantity(db, user_id, product_id, quantity, session_id)

    # 计算总数量和总价
    total_quantity = sum(item.quantity for item in cart.items)
    total_price = sum(
        (item.product.price or 0) * item.quantity
        for item in cart.items if item.product
    )

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=[
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": item.product
            }
            for item in cart.items
        ],
        total_quantity=total_quantity,
        total_price=round(total_price, 2),
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

@app.delete("/cart", response_model=CartResponse)
async def clear_cart_endpoint(
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """清空购物车"""
    cart = clear_cart(db, user_id, session_id)

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        session_id=cart.session_id,
        items=[],
        total_quantity=0,
        total_price=0.0,
        created_at=cart.created_at,
        updated_at=cart.updated_at
    )

# ============= 收藏相关 =============
@app.get("/wishlist", response_model=WishlistResponse)
async def get_wishlist_endpoint(
    user_id: int = 1,
    db = Depends(get_db)
):
    """获取收藏列表"""
    wishlist_items = get_wishlist(db, user_id)

    return WishlistResponse(
        items=[
            {
                "id": item.id,
                "user_id": item.user_id,
                "session_id": item.session_id,
                "product_id": item.product_id,
                "product": item.product,
                "created_at": item.created_at
            }
            for item in wishlist_items
        ],
        total_count=len(wishlist_items)
    )

@app.post("/wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_to_wishlist_endpoint(
    product_id: int,
    user_id: int = 1,
    session_id: Optional[str] = None,
    db = Depends(get_db)
):
    """添加商品到收藏"""
    # 验证商品是否存在
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="商品不存在"
        )

    wishlist_item = add_to_wishlist(db, user_id, product_id, session_id)
    return {"message": "添加成功", "id": wishlist_item.id}

@app.delete("/wishlist/{product_id}")
async def remove_from_wishlist_endpoint(
    product_id: int,
    user_id: int = 1,
    db = Depends(get_db)
):
    """从收藏移除商品"""
    success = remove_from_wishlist(db, user_id, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="收藏项不存在"
        )
    return {"message": "删除成功"}

@app.get("/wishlist/check/{product_id}")
async def check_wishlist_endpoint(
    product_id: int,
    user_id: int = 1,
    db = Depends(get_db)
):
    """检查商品是否已收藏"""
    is_in_wishlist = is_product_in_wishlist(db, user_id, product_id)
    return {"is_in_wishlist": is_in_wishlist}

# ============= 对话历史导出相关 =============
@app.post("/chat/export")
async def export_chat_history_endpoint(
    request: ExportHistoryRequest,
    db = Depends(get_db)
):
    """导出对话历史"""
    result = export_chat_history(db, request.session_ids)  # 移除多余的"json"参数

    if "error" in result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"]
        )

    return Response(
        content=result["content"],
        media_type=result["content_type"],
        headers={
            "Content-Disposition": f"attachment; filename={result['filename']}"
        }
    )

# ============= 数据分析统计相关 =============
@app.get("/analytics/overview", response_model=AnalyticsReport)
async def get_analytics_report_endpoint(user_id: int = 1, db = Depends(get_db)):
    """获取综合分析报告"""
    report = get_analytics_report(db, user_id)
    return report

@app.get("/analytics/sessions", response_model=SessionStatistics)
async def get_session_statistics_endpoint(user_id: int = 1, db = Depends(get_db)):
    """获取会话统计"""
    return get_session_statistics(db, user_id)

@app.get("/analytics/behavior", response_model=UserBehaviorStatistics)
async def get_user_behavior_endpoint(user_id: int = 1, db = Depends(get_db)):
    """获取用户行为统计"""
    return get_user_behavior_statistics(db, user_id)

@app.get("/analytics/top-products", response_model=List[ProductRankingItem])
async def get_top_products_endpoint(user_id: int = 1, limit: int = 10, db = Depends(get_db)):
    """获取热门商品排行"""
    return get_top_products(db, user_id, limit)

@app.get("/analytics/intents", response_model=List[IntentDistributionItem])
async def get_intent_distribution_endpoint(user_id: int = 1, db = Depends(get_db)):
    """获取意图分布"""
    return get_intent_distribution(db, user_id)

@app.get("/analytics/export")
async def export_analytics_report_endpoint(user_id: int = 1, db = Depends(get_db)):
    """导出分析报告（JSON格式）"""
    report = get_analytics_report(db, user_id)
    
    # 添加自定义的JSON编码器来处理AnalyticsReport对象
    class AnalyticsReportEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (SessionStatistics, UserBehaviorStatistics, ProductRankingItem, IntentDistributionItem)):
                return obj.__dict__
            return super().default(obj)
    
    content = json.dumps(report, ensure_ascii=False, indent=2, cls=AnalyticsReportEncoder)

    return Response(
        content=content,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=analytics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        }
    )
