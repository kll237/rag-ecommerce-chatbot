"""
CRUD操作
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from .db_models import User, ChatSession, ChatMessage, Product, Feedback, Cart, CartItem, Wishlist
from .schemas import UserCreate, ChatSessionCreate, ChatMessageCreate, FeedbackCreate, SessionStatistics, UserBehaviorStatistics, ProductRankingItem, IntentDistributionItem, AnalyticsReport
import uuid
from sqlalchemy import func, and_
from datetime import datetime

def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> Optional[User]:
    """获取用户"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """根据用户名获取用户"""
    return db.query(User).filter(User.username == username).first()

def create_chat_session(db: Session, user_id: int, title: Optional[str] = None, session_id: Optional[str] = None) -> ChatSession:
    """创建聊天会话"""
    if not session_id:
        session_id = str(uuid.uuid4())
    if not title:
        title = f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    db_session = ChatSession(
        user_id=user_id,
        session_id=session_id,
        title=title
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_sessions(db: Session, user_id: int) -> List[ChatSession]:
    """获取用户的所有会话"""
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

def get_chat_session_by_id(db: Session, session_id: int) -> Optional[ChatSession]:
    """获取指定会话"""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def delete_chat_session(db: Session, session_id: int) -> bool:
    """删除聊天会话"""
    # 先删除会话的所有消息
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    # 删除会话
    result = db.query(ChatSession).filter(ChatSession.id == session_id).delete()
    db.commit()
    return result > 0

def delete_chat_sessions(db: Session, session_ids: List[int]) -> int:
    """批量删除聊天会话"""
    # 删除所有指定会话的消息
    db.query(ChatMessage).filter(ChatMessage.session_id.in_(session_ids)).delete()
    # 删除会话
    result = db.query(ChatSession).filter(ChatSession.id.in_(session_ids)).delete()
    db.commit()
    return result

def create_chat_message(
    db: Session,
    session_id: int,
    role: str,
    content: str,
    intent: Optional[str] = None,
    confidence: Optional[float] = None,
    retrieved_docs: Optional[str] = None
) -> ChatMessage:
    """创建聊天消息"""
    db_message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        intent=intent,
        confidence=confidence,
        retrieved_docs=retrieved_docs
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, session_id: int) -> List[ChatMessage]:
    """获取会话的所有消息"""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()

def search_products(
    db: Session,
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 10
) -> List[Product]:
    """搜索商品"""
    q = db.query(Product)

    if query:
        q = q.filter(
            (Product.name.contains(query)) |
            (Product.description.contains(query))
        )

    if category:
        q = q.filter(Product.category == category)

    if min_price is not None:
        q = q.filter(Product.price >= min_price)

    if max_price is not None:
        q = q.filter(Product.price <= max_price)

    return q.limit(limit).all()

def get_product_by_id(db: Session, product_id: int) -> Optional[Product]:
    """获取商品详情"""
    return db.query(Product).filter(Product.id == product_id).first()

def get_product_by_product_id(db: Session, product_id: str) -> Optional[Product]:
    """通过product_id获取商品详情"""
    return db.query(Product).filter(Product.product_id == product_id).first()

def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
    """创建反馈"""
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

# ============= 购物车相关 =============
def get_or_create_cart(db: Session, user_id: int, session_id: Optional[str] = None) -> Cart:
    """获取或创建购物车"""
    # 如果有session_id，先尝试通过session_id查找
    if session_id:
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if cart:
            return cart

    # 通过user_id查找
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(
            user_id=user_id,
            session_id=session_id
        )
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def add_to_cart(db: Session, user_id: int, product_id: int, quantity: int, session_id: Optional[str] = None) -> Cart:
    """添加商品到购物车"""
    cart = get_or_create_cart(db, user_id, session_id)

    # 检查商品是否已在购物车
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)
    return cart

def remove_from_cart(db: Session, user_id: int, product_id: int, session_id: Optional[str] = None) -> Cart:
    """从购物车移除商品"""
    cart = get_or_create_cart(db, user_id, session_id)

    # 删除指定商品
    db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).delete()

    db.commit()
    db.refresh(cart)
    return cart

def update_cart_item_quantity(db: Session, user_id: int, product_id: int, quantity: int, session_id: Optional[str] = None) -> Cart:
    """更新购物车商品数量"""
    cart = get_or_create_cart(db, user_id, session_id)

    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if cart_item:
        if quantity <= 0:
            # 数量为0或负数则删除
            db.delete(cart_item)
        else:
            cart_item.quantity = quantity

    db.commit()
    db.refresh(cart)
    return cart

def clear_cart(db: Session, user_id: int, session_id: Optional[str] = None) -> Cart:
    """清空购物车"""
    cart = get_or_create_cart(db, user_id, session_id)

    # 删除所有购物车项
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()

    db.commit()
    db.refresh(cart)
    return cart

def get_cart(db: Session, user_id: int, session_id: Optional[str] = None) -> Optional[Cart]:
    """获取购物车"""
    if session_id:
        cart = db.query(Cart).filter(Cart.session_id == session_id).first()
        if cart:
            return cart

    return db.query(Cart).filter(Cart.user_id == user_id).first()

# ============= 收藏相关 =============
def add_to_wishlist(db: Session, user_id: int, product_id: int, session_id: Optional[str] = None) -> Wishlist:
    """添加商品到收藏"""
    # 检查是否已收藏
    existing = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first()

    if existing:
        return existing

    wishlist_item = Wishlist(
        user_id=user_id,
        product_id=product_id,
        session_id=session_id
    )
    db.add(wishlist_item)
    db.commit()
    db.refresh(wishlist_item)
    return wishlist_item

def remove_from_wishlist(db: Session, user_id: int, product_id: int) -> bool:
    """从收藏移除商品"""
    result = db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).delete()

    db.commit()
    return result > 0

def get_wishlist(db: Session, user_id: int) -> List[Wishlist]:
    """获取收藏列表"""
    return db.query(Wishlist).filter(
        Wishlist.user_id == user_id
    ).order_by(Wishlist.created_at.desc()).all()

def is_product_in_wishlist(db: Session, user_id: int, product_id: int) -> bool:
    """检查商品是否在收藏中"""
    return db.query(Wishlist).filter(
        Wishlist.user_id == user_id,
        Wishlist.product_id == product_id
    ).first() is not None

# ============= 对话历史导出相关 =============
def export_chat_history(db: Session, session_ids: Optional[List[int]] = None) -> dict:
    """导出聊天历史"""
    query = db.query(ChatSession)

    if session_ids:
        query = query.filter(ChatSession.id.in_(session_ids))

    sessions = query.all()

    export_data = []
    for session in sessions:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()

        session_data = {
            "session_id": session.session_id,
            "title": session.title,
            "created_at": session.created_at.isoformat(),
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "intent": msg.intent,
                    "confidence": msg.confidence,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
        export_data.append(session_data)

    return {
        "export_time": datetime.now().isoformat(),
        "total_sessions": len(sessions),
        "sessions": export_data
    }

# ============= 数据统计分析相关 =============
def get_session_statistics(db: Session, user_id: Optional[int] = None) -> SessionStatistics:
    """获取会话统计数据"""
    # 基础查询
    sessions_query = db.query(ChatSession)
    messages_query = db.query(ChatMessage)
    users_query = db.query(User)

    # 如果指定了user_id，则只统计该用户的数据
    if user_id is not None:
        sessions_query = sessions_query.filter(ChatSession.user_id == user_id)
        messages_query = messages_query.join(ChatSession).filter(ChatSession.user_id == user_id)

    total_sessions = sessions_query.count()

    # 今日会话数
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_sessions = sessions_query.filter(ChatSession.created_at >= today_start).count()

    # 总消息数
    total_messages = messages_query.count()

    # 平均每会话消息数
    avg_messages = total_messages / total_sessions if total_sessions > 0 else 0

    # 总用户数
    total_users = users_query.count()

    return SessionStatistics(
        total_sessions=total_sessions,
        today_sessions=today_sessions,
        total_messages=total_messages,
        avg_messages_per_session=round(avg_messages, 2),
        total_users=total_users
    )

def get_user_behavior_statistics(db: Session, user_id: Optional[int] = None) -> UserBehaviorStatistics:
    """获取用户行为统计数据"""
    # 购物车操作次数（基于CartItem表）
    cart_query = db.query(CartItem)
    if user_id is not None:
        cart_query = cart_query.join(Cart).filter(Cart.user_id == user_id)
    total_cart_operations = cart_query.count()

    # 收藏操作次数
    wishlist_query = db.query(Wishlist)
    if user_id is not None:
        wishlist_query = wishlist_query.filter(Wishlist.user_id == user_id)
    total_wishlist_operations = wishlist_query.count()

    # 商品查看次数（这里用消息数作为近似）
    messages_query = db.query(ChatMessage).filter(ChatMessage.role == 'user')
    if user_id is not None:
        messages_query = messages_query.join(ChatSession).filter(ChatSession.user_id == user_id)
    total_product_views = messages_query.count()

    # 反馈提交次数
    feedback_query = db.query(Feedback)
    if user_id is not None:
        feedback_query = feedback_query.join(ChatMessage).join(ChatSession).filter(ChatSession.user_id == user_id)
    total_feedbacks = feedback_query.count()

    return UserBehaviorStatistics(
        total_cart_operations=total_cart_operations,
        total_wishlist_operations=total_wishlist_operations,
        total_product_views=total_product_views,
        total_feedbacks=total_feedbacks
    )

def get_top_products(db: Session, user_id: Optional[int] = None, limit: int = 10) -> List[ProductRankingItem]:
    """获取热门商品排行"""
    # 通过购物车和收藏次数来统计热门商品
    cart_counts = db.query(
        CartItem.product_id,
        func.count(CartItem.id).label('cart_count')
    ).join(Cart, CartItem.cart_id == Cart.id)

    if user_id is not None:
        cart_counts = cart_counts.filter(Cart.user_id == user_id)

    cart_counts = cart_counts.group_by(CartItem.product_id).all()

    wishlist_counts = db.query(
        Wishlist.product_id,
        func.count(Wishlist.id).label('wishlist_count')
    )

    if user_id is not None:
        wishlist_counts = wishlist_counts.filter(Wishlist.user_id == user_id)

    wishlist_counts = wishlist_counts.group_by(Wishlist.product_id).all()

    # 合并计数
    product_scores = {}
    for pid, count in cart_counts:
        product_scores[pid] = {'cart_count': count, 'wishlist_count': 0}

    for pid, count in wishlist_counts:
        if pid in product_scores:
            product_scores[pid]['wishlist_count'] = count
        else:
            product_scores[pid] = {'cart_count': 0, 'wishlist_count': count}

    # 计算热度值并排序
    ranking = []
    for product_id, counts in product_scores.items():
        popularity_score = counts['cart_count'] * 2 + counts['wishlist_count'] * 1  # 购物车权重更高

        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            ranking.append(ProductRankingItem(
                product_id=product.id,
                name=product.name,
                category=product.category,
                price=product.price,
                popularity_score=popularity_score,
                cart_count=counts['cart_count'],
                wishlist_count=counts['wishlist_count']
            ))

    # 按热度值排序
    ranking.sort(key=lambda x: x.popularity_score, reverse=True)

    return ranking[:limit]

def get_intent_distribution(db: Session, user_id: Optional[int] = None) -> List[IntentDistributionItem]:
    """获取意图分布"""
    query = db.query(
        ChatMessage.intent,
        func.count(ChatMessage.id).label('count')
    ).filter(
        ChatMessage.intent.isnot(None),
        ChatMessage.role == 'user'  # 只统计用户消息的意图
    ).group_by(ChatMessage.intent)

    # 如果指定了user_id，则只统计该用户的数据
    if user_id is not None:
        query = query.join(ChatSession).filter(ChatSession.user_id == user_id)

    results = query.all()

    total_count = sum(r.count for r in results)

    distribution = []
    for result in results:
        percentage = (result.count / total_count * 100) if total_count > 0 else 0
        distribution.append(IntentDistributionItem(
            intent=result.intent or '未知',
            count=result.count,
            percentage=round(percentage, 2)
        ))

    # 按次数排序
    distribution.sort(key=lambda x: x.count, reverse=True)

    return distribution

def get_analytics_report(db: Session, user_id: Optional[int] = None) -> AnalyticsReport:
    """获取综合分析报告"""
    session_stats = get_session_statistics(db, user_id)
    user_behavior = get_user_behavior_statistics(db, user_id)
    top_products = get_top_products(db, user_id, limit=10)
    intent_distribution = get_intent_distribution(db, user_id)

    return AnalyticsReport(
        session_stats=session_stats,
        user_behavior=user_behavior,
        top_products=top_products,
        intent_distribution=intent_distribution,
        generated_at=datetime.now()
    )