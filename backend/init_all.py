"""
一键初始化数据库和商品数据
运行此脚本后重启后端服务即可
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import init_db
from init_products import init_products

def main():
    print("=" * 60)
    print("开始初始化数据库和商品数据...")
    print("=" * 60)

    # 1. 初始化数据库表结构
    print("\n[1/2] 初始化数据库表结构...")
    try:
        init_db()
        print("✅ 数据库表结构初始化完成")
    except Exception as e:
        print(f"❌ 数据库表结构初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 2. 导入商品数据
    print("\n[2/2] 导入商品数据...")
    try:
        init_products()
        print("✅ 商品数据导入完成")
    except Exception as e:
        print(f"❌ 商品数据导入失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✅ 初始化完成！")
    print("=" * 60)
    print("\n📋 下一步操作：")
    print("  1. 停止后端服务（如果正在运行）")
    print("  2. 重新启动后端服务")
    print("\n启动命令：")
    print("  python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
    print("\n或者在 PyCharm 中：")
    print("  - 右键点击 main.py -> Run 'main'")

if __name__ == "__main__":
    main()
