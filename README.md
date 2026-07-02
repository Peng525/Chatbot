# Chatbot — Telegram + Azure OpenAI 聊天机器人

基于 [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) 与 Azure OpenAI Chat Completions API 构建的 Telegram 文本聊天机器人。用户向 Bot 发送消息后，程序会调用大模型生成回复，并以「思考中...」占位消息的形式异步更新结果。

## 功能特性

- 接收 Telegram 纯文本消息（自动忽略 `/` 开头的命令）
- 调用 Azure OpenAI 部署的 GPT 模型生成回复
- 回复前先发送「思考中...」，生成完成后编辑为最终内容
- 支持本地运行与 GitHub Actions 自动部署至 AWS EC2

## 项目结构

```
Chatbot/
├── chatbot.py              # Telegram Bot 主程序入口
├── ChatGPT_25.py           # Azure OpenAI API 客户端封装
├── config.ini              # 本地配置文件（含密钥，勿提交到 Git）
├── config.ini.example      # 配置文件模板（可安全提交）
├── requirements.txt        # Python 依赖
├── test.py                 # 简单测试脚本
└── .github/
    └── workflows/
        └── deploy.yml      # 推送到 main 分支时自动部署到 EC2
```

## 环境要求

- Python 3.10+
- Telegram Bot Token（通过 [@BotFather](https://t.me/BotFather) 创建）
- Azure OpenAI 服务及已部署的模型

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Peng525/Chatbot.git
cd Chatbot
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. 配置 `config.ini`

复制模板并填入你自己的密钥（**请勿将真实密钥写入 README 或提交到 Git**）：

```bash
cp config.ini.example config.ini
```

`config.ini` 格式如下：

```ini
[TELEGRAM]
ACCESS_TOKEN = your_telegram_bot_token_here

[CHATGPT]
API_KEY = your_azure_openai_api_key_here
BASE_URL = https://your-resource-name.openai.azure.com
MODEL = your-deployment-name
API_VER = 2024-02-15-preview
```

| 配置项 | 说明 |
|--------|------|
| `ACCESS_TOKEN` | Telegram Bot Token |
| `API_KEY` | Azure OpenAI API Key |
| `BASE_URL` | Azure OpenAI 资源 Endpoint 地址 |
| `MODEL` | Azure 上的模型部署名称（Deployment Name） |
| `API_VER` | Azure OpenAI API 版本号 |

### 4. 启动机器人

```bash
python chatbot.py
```

启动成功后，在 Telegram 中找到你的 Bot 并发送文本消息即可测试。

### 5. 单独测试大模型接口（可选）

不启动 Telegram Bot，仅测试 Azure OpenAI 调用：

```bash
python ChatGPT_25.py
```

程序会进入交互式 REPL，输入问题后回车即可查看模型回复。

## 工作原理

```
用户 (Telegram)
    │
    ▼
chatbot.py ── 长轮询接收消息
    │
    ├── 回复「思考中...」
    │
    ▼
ChatGPT_25.py ── POST /deployments/{model}/chat/completions
    │
    ▼
Azure OpenAI ── 返回生成内容
    │
    ▼
编辑消息为最终回复
```

- **系统提示词**：面向大学生用户，要求回复口语化、信息丰富、用词简单、表达直接。
- **生成参数**：`temperature=1`，`max_tokens=150`，非流式输出。

## 自动部署（GitHub Actions → AWS EC2）

向 `main` 分支推送代码后，`.github/workflows/deploy.yml` 会自动：

1. 通过 SSH 连接 EC2 实例
2. 拉取最新代码
3. 激活虚拟环境并更新依赖
4. 停止旧进程，后台启动新版 `chatbot.py`

### 需要在 GitHub 仓库中配置的 Secrets

在 **Settings → Secrets and variables → Actions** 中添加：

| Secret 名称 | 说明 |
|-------------|------|
| `EC2_SSH_KEY` | 连接 EC2 的 SSH 私钥 |
| `EC2_USER` | EC2 登录用户名（如 `ubuntu`） |
| `EC2_HOST` | EC2 公网 IP 或域名 |

> **注意**：Secrets 仅存储在 GitHub，不会出现在代码或 README 中。EC2 服务器上需提前放置好 `config.ini` 与 Python 虚拟环境。

### EC2 服务器前置条件

- 已克隆本仓库至 `~/ChatBot_Telegram/Chatbot`
- 已创建虚拟环境并安装依赖
- 已在项目目录下配置 `config.ini`（含有效 Token 与 API Key）

## 依赖说明

| 包名 | 用途 |
|------|------|
| `python-telegram-bot==22.5` | Telegram Bot SDK |
| `requests` | 调用 Azure OpenAI REST API |
| `urllib3==2.6.2` | HTTP 库（版本锁定） |
| `configparser` | 读取 INI 配置文件 |

## 安全提示

- **切勿**将 `config.ini`、`.env` 或任何含 API Key / Bot Token 的文件提交到 Git
- 本仓库已通过 `.gitignore` 忽略 `config.ini`；请始终使用 `config.ini.example` 作为模板
- 若密钥泄露，请立即在 Telegram BotFather 与 Azure Portal 中轮换密钥

## 常见问题

**Q: 机器人无响应？**  
检查 `config.ini` 中的 `ACCESS_TOKEN` 是否正确，以及进程是否已在运行（EC2 上避免多实例抢占同一 Token）。

**Q: 返回「大模型调用错误」？**  
确认 Azure OpenAI 的 `API_KEY`、`BASE_URL`、`MODEL`、`API_VER` 配置正确，且账户有足够配额。

**Q: 部署后旧 Bot 仍在运行？**  
工作流会通过 `pkill -f "python chatbot.py"` 清理旧进程；若路径不同，请相应调整 `deploy.yml`。

## 许可证

本项目仅供学习与个人使用。使用前请遵守 Telegram 与 Azure OpenAI 的服务条款。
