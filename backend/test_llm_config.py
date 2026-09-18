"""
测试大模型配置
"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("❌ OpenAI库未安装")
    print("请运行: pip install openai")
    sys.exit(1)

from app.config import config

print("=" * 60)
print("大模型配置检查")
print("=" * 60)

# 1. 检查环境变量
print("\n1. 环境变量检查:")
print(f"   OPENAI_API_KEY: {'***已配置***' if config.OPENAI_API_KEY else '❌ 未配置'}")
if config.OPENAI_API_KEY:
    print(f"   前20位: {config.OPENAI_API_KEY[:20]}...")
print(f"   OPENAI_MODEL: {config.OPENAI_MODEL}")
print(f"   OPENAI_BASE_URL: {config.OPENAI_BASE_URL or '默认(https://api.openai.com/v1)'}")

# 2. 测试API调用
if config.OPENAI_API_KEY:
    print("\n2. 测试API调用:")

    try:
        # 设置API key
        if config.OPENAI_BASE_URL:
            openai.base_url = config.OPENAI_BASE_URL
        openai.api_key = config.OPENAI_API_KEY

        # 发送测试请求
        print("   发送测试请求...")
        response = openai.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "你是一个测试助手。"},
                {"role": "user", "content": "你好，请回复'测试成功'"}
            ],
            max_tokens=50,
            timeout=10
        )

        result = response.choices[0].message.content.strip()
        print(f"   ✅ API调用成功")
        print(f"   返回内容: {result}")
        print(f"   模型: {response.model}")
        print(f"   Token使用: {response.usage.total_tokens}")

    except Exception as e:
        print(f"   ❌ API调用失败: {type(e).__name__}: {e}")
        print("\n   常见问题:")
        print("   1. API Key错误 - 检查OPENAI_API_KEY是否正确")
        print("   2. Base URL错误 - 检查OPENAI_BASE_URL是否正确")
        print("   3. 网络问题 - 检查是否可以访问API服务器")
        print("   4. 模型不存在 - 检查OPENAI_MODEL是否正确")
        sys.exit(1)

else:
    print("\n2. ⚠️ OPENAI_API_KEY未配置，无法测试API调用")
    print("\n配置方法:")
    print("   创建 .env 文件并添加:")
    print("   OPENAI_API_KEY=your-api-key-here")
    print("   OPENAI_MODEL=gpt-3.5-turbo  # 或其他模型")
    print("   OPENAI_BASE_URL=https://api.openai.com/v1  # 可选")

print("\n" + "=" * 60)
print("配置检查完成")
print("=" * 60)
