# 🌈 彩虹一号 AI 日报系统

彩虹一号是一个自动化的AI产品监控与日报生成系统，专门监控Product Hunt等平台的AI相关产品，并生成结构化的中文日报推送到飞书。

## ✨ 功能特性

### 📊 数据采集
- **Product Hunt监控**: 自动抓取每日Top Products Launching Today
- **多源扩展**: 支持后续添加Hacker News、GitHub Trending等信息源
- **智能去重**: 避免相同产品在不同源中重复出现

### 🤖 AI智能分析
- **相关性判断**: 使用GPT-4分析产品的AI相关性（0-1评分）
- **内容翻译**: 自动将英文内容翻译为中文
- **深度分析**: 提取应用场景、技术实现、产品意义等信息
- **趋势总结**: 生成每日AI产品趋势分析

### 📝 日报生成
- **结构化格式**: 按照预设模板生成专业日报
- **多种输出**: 支持Markdown和JSON格式
- **丰富内容**: 包含产品排名、功能介绍、应用场景等详细信息

### 📱 飞书推送
- **实时推送**: 自动推送日报到飞书群聊
- **富文本卡片**: 美观的飞书交互式卡片格式
- **多种通知**: 支持启动通知、错误通知等

### ⏰ 定时任务
- **灵活调度**: 可配置数据收集和报告发送时间
- **健康监控**: 定期系统健康检查
- **手动触发**: 支持立即执行任务

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <project-url>
cd AI_daily

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板：
```bash
cp .env.template .env
```

编辑 `.env` 文件，填入必要的API密钥：

```bash
# OpenAI API配置
OPENAI_API_KEY=sk-your-openai-api-key

# 飞书配置（二选一）
# 方式1: 使用Webhook（推荐）
FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/your-webhook-url

# 方式2: 使用应用API
# FEISHU_APP_ID=your-app-id
# FEISHU_APP_SECRET=your-app-secret

# 可选配置
LOG_LEVEL=INFO
ENVIRONMENT=production
```

### 3. 配置系统参数

编辑 `config.yaml` 文件，调整系统配置：

```yaml
# 定时任务配置
schedule:
  daily_report_time: "09:00"  # 每日报告发送时间
  data_collection_time: "08:00"  # 数据收集时间

# 输出配置
output:
  max_products: 10  # 每日最多包含产品数量
  
# AI配置
ai:
  model: "gpt-4"  # 使用的AI模型
  temperature: 0.3
```

### 4. 运行系统

#### 检查配置
```bash
python main.py --mode config
```

#### 发送测试消息
```bash
python main.py --mode test
```

#### 执行一次完整任务
```bash
python main.py --mode once
```

#### 启动定时任务模式
```bash
python main.py --mode scheduler
```

#### 查看系统状态
```bash
python main.py --mode status
```

## 📋 日报格式

系统按照以下格式生成AI产品日报：

```
大标题：产品标题 - 一句话介绍
- 排名：具体排名多少
- 项目名称：即产品名称
- 详细功能介绍：即产品介绍（包括网页里面的介绍和创始人的介绍）
- 应用场景：AI应用的具体场景
- 技术实现方式：技术架构和实现方法
- 产品意义和应用前景：产品价值和发展前景分析
- 原始链接：Product Hunt链接和产品官网
```

## 🛠️ 系统架构

```
AI_daily/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── config.py          # 配置管理
│   ├── models.py          # 数据模型
│   ├── main_service.py    # 主服务
│   ├── scheduler.py       # 定时任务调度器
│   ├── ai_analyzer.py     # AI分析器
│   ├── report_generator.py # 日报生成器
│   ├── feishu_sender.py   # 飞书推送器
│   └── scrapers/          # 数据抓取器
│       ├── __init__.py
│       └── product_hunt.py # Product Hunt抓取器
├── main.py                # 主程序入口
├── config.yaml           # 系统配置文件
├── requirements.txt      # Python依赖
├── .env.template        # 环境变量模板
└── README.md           # 项目文档
```

## 🔧 配置说明

### config.yaml 配置项

- **app**: 应用基本信息配置
- **sources**: 信息源配置（Product Hunt等）
- **ai**: AI分析配置（模型、温度等）
- **filtering**: 内容筛选配置（关键词等）
- **feishu**: 飞书推送配置
- **schedule**: 定时任务配置
- **output**: 输出格式配置

### 环境变量

- **OPENAI_API_KEY**: OpenAI API密钥（必需）
- **FEISHU_WEBHOOK_URL**: 飞书Webhook地址（推荐）
- **FEISHU_APP_ID**: 飞书应用ID（可选）
- **FEISHU_APP_SECRET**: 飞书应用密钥（可选）
- **LOG_LEVEL**: 日志级别（INFO/DEBUG/WARNING）

## 📊 日志和监控

### 日志文件
- 系统日志保存在 `rainbow_one.log` 文件中
- 支持按日志级别过滤
- 包含详细的运行状态和错误信息

### 报告存储
- Markdown格式: `reports/ai_daily_report_YYYYMMDD.md`
- JSON格式: `reports/ai_daily_report_YYYYMMDD.json`

### 监控功能
- 定期健康检查
- 错误自动通知
- 运行状态查询

## 🔄 扩展功能

### 新增信息源
1. 在 `src/scrapers/` 目录下创建新的抓取器
2. 实现标准的数据抓取接口
3. 在配置文件中添加相应配置

### 自定义AI分析
1. 修改 `ai_analyzer.py` 中的分析逻辑
2. 调整相关性评分标准
3. 添加新的分析维度

### 其他推送渠道
1. 参考 `feishu_sender.py` 的实现
2. 创建新的推送器类
3. 在主服务中集成新的推送方式

## ❓ 常见问题

### Q: 如何获取OpenAI API密钥？
A: 访问 [OpenAI官网](https://platform.openai.com) 注册账号并创建API密钥。

### Q: 如何配置飞书Webhook？
A: 在飞书群聊中添加自定义机器人，获取Webhook地址。

### Q: 系统支持哪些AI模型？
A: 支持OpenAI的所有文本模型，推荐使用GPT-4以获得更好的分析效果。

### Q: 可以修改日报格式吗？
A: 可以，修改 `report_generator.py` 中的格式化函数即可。

### Q: 如何部署到服务器？
A: 可以使用cron、systemd或Docker等方式部署定时任务。

## 🤝 贡献指南

欢迎提交Issues和Pull Requests来改进这个项目！

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系我们。

---

*彩虹一号 - 让AI产品信息触手可及* 🌈 