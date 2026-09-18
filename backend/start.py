"""
启动脚本 - Windows兼容版
"""
import sys
import os
import signal
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()

# 设置环境变量禁用某些可能导致问题的优化
# 这可以减少 Fortran 运行时错误
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('MKL_NUM_THREADS', '1')

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def signal_handler(sig, frame):
    """优雅退出处理"""
    print("\n\n正在关闭服务...")
    sys.exit(0)

# 注册信号处理器（Unix系统）
if hasattr(signal, 'SIGINT'):
    signal.signal(signal.SIGINT, signal_handler)
if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, signal_handler)

try:
    import uvicorn
    from app.config import config

    print("=" * 60)
    print("启动电商RAG客服系统...")
    print("=" * 60)
    print(f"API地址: http://{config.API_HOST}:{config.API_PORT}")
    print(f"文档地址: http://{config.API_HOST}:{config.API_PORT}/docs")
    print(f"前端地址: http://localhost:5173")
    print("=" * 60)

    # 调试信息：检查豆包API Key配置
    is_configured = config.DOUBAO_API_KEY and config.DOUBAO_API_KEY not in ["your-doubao-api-key", "your-doubao-api-key-here"]
    print(f"\n[调试信息] 豆包API Key: {'***已配置***' if is_configured else '❌ 未配置或为默认值'}")
    if is_configured:
        print(f"[调试信息] API Key前20位: {config.DOUBAO_API_KEY[:20]}...")
    print(f"[调试信息] 使用模型: {config.DOUBAO_ASR_MODEL}")

    print("\n按 Ctrl+C 停止服务\n")

    # Windows上禁用reload模式，避免multiprocessing错误
    if __name__ == '__main__':
        try:
            uvicorn.run(
                "app.main:app",
                host=config.API_HOST,
                port=config.API_PORT,
                reload=False,  # Windows上禁用reload
                log_level="info"
            )
        except KeyboardInterrupt:
            # Windows上按 Ctrl+C 会触发这个异常
            print("\n\n正在关闭服务...")
            # 立即退出，避免 FAISS/MKL 清理错误
            os._exit(0)
        except SystemExit:
            # 正常退出
            print("\n服务已关闭")
        except Exception as e:
            print(f"\n启动失败: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

except ImportError as e:
    print(f"错误: 缺少依赖包 - {e}")
    print("\n请先安装依赖:")
    print("pip install -r requirements.txt")
    sys.exit(1)