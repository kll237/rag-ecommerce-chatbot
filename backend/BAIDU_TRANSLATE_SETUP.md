# 百度翻译 API 配置说明

## 获取百度翻译 API Key

### 步骤 1：注册百度开发者账号
1. 访问百度翻译开放平台：https://fanyi-api.baidu.com/
2. 点击右上角"登录/注册"，使用百度账号登录或注册

### 步骤 2：开通翻译服务
1. 登录后进入"管理控制台"
2. 点击"开通服务"
3. 选择"通用翻译API"标准版
4. 按照提示完成开通（免费版每月 5 万字符）

### 步骤 3：获取 API 凭证
1. 在控制台左侧菜单找到"开发者信息"
2. 您将看到：
   - **APP ID**：应用 ID
   - **密钥**：Secret Key

### 步骤 4：配置到项目中
在 `backend/.env` 文件中添加以下配置：

```env
BAIDU_TRANSLATE_APP_ID=您的APP_ID
BAIDU_TRANSLATE_SECRET_KEY=您的密钥