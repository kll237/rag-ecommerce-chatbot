# 电商RAG客服系统 - 快速启动指南

## 🚀 快速启动

### 方法一：使用批处理脚本（推荐）

#### 1. 一键启动（同时启动前后端）
```bash
run_all.bat
```
然后选择选项 `3` 即可同时启动前后端服务。

#### 2. 分别启动
**启动后端：**
```bash
start_backend.bat
```

**启动前端（新开一个终端）：**
```bash
cd frontend
npm run dev
```

---

### 方法二：使用命令行

#### 步骤1：激活虚拟环境
```powershell
conda activate rag_cs
```

#### 步骤2：安装后端依赖
```powershell
cd backend
pip install -r requirements.txt
```

#### 步骤3：启动后端
```powershell
python start.py
```

#### 步骤4：新开一个终端，启动前端
```powershell
conda activate rag_cs
cd D:\znds\ecommerce_rag\frontend
npm install
npm run dev
```

---

### 方法三：使用PyCharm

#### 启动后端：
1. 在PyCharm中打开 `backend/start.py`
2. 右键点击 → `Run 'start'`

#### 启动前端：
1. 打开PyCharm Terminal
2. 运行：`cd frontend && npm run dev`

---

## 📍 访问地址

- **前端应用**: http://localhost:5173
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

---

## ❓ 常见问题

### 1. 后端启动失败
**症状**：运行 `python start.py` 后立即退出

**解决方案**：
```powershell
# 检查依赖是否安装
pip list | grep fastapi

# 重新安装依赖
pip install -r requirements.txt
```

### 2. 前端端口被占用
**症状**：运行 `npm run dev` 提示端口 5173 被占用

**解决方案**：
```powershell
# 使用其他端口
npm run dev -- --port 5174
```

### 3. 找不到模块
**症状**：`ModuleNotFoundError: No module named 'xxx'`

**解决方案**：
```powershell
# 确保在backend目录下
cd D:\znds\ecommerce_rag\backend

# 安装缺失的包
pip install <包名>
```

### 4. 权限问题（Windows）
**症状**：启动时提示权限不足

**解决方案**：
以管理员身份运行PowerShell

---

## 🛠️ 技术支持

如果遇到其他问题：
1. 检查Python版本：需要 Python 3.8+
2. 检查Node.js版本：需要 Node.js 16+
3. 确保虚拟环境已激活：`conda activate rag_cs`
4. 查看错误日志

---

## 📝 使用说明

1. 访问 http://localhost:5173
2. 点击 "+ 新对话" 开始聊天
3. 输入问题，系统会基于知识库回答
4. 支持产品查询、订单咨询、FAQ等

---

## 🎯 测试用例

可以尝试以下问题：
- "你们的产品质量怎么样？"
- "发货需要多长时间？"
- "支持哪些支付方式？"
- "可以退货吗？"
- "推荐几款手机"
