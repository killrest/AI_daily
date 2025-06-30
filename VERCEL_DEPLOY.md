# 🌈 彩虹一号 AI 日报 - Vercel 部署指南

## 📋 部署步骤

### 1. 准备工作
确保您已经安装了 [Node.js](https://nodejs.org/) 和 npm。

### 2. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 3. 登录 Vercel
```bash
vercel login
```

### 4. 配置环境变量
在部署前，您需要在 Vercel 上设置以下环境变量：

#### 必需的环境变量：
- `AI_API_KEY`: 您的火山引擎ARK平台API密钥
- `FEISHU_WEBHOOK_URL`: 飞书机器人的Webhook URL
- `FEISHU_WEBHOOK_SECRET`: 飞书机器人的签名密钥

#### 可选环境变量：
- `AI_BASE_URL`: AI API的基础URL (默认: https://ark.cn-beijing.volces.com/api/v3)
- `AI_ENDPOINT_ID`: 火山引擎ARK的端点ID

### 5. 部署到 Vercel
在项目根目录运行：
```bash
vercel --prod
```

### 6. 设置环境变量
您可以通过以下方式设置环境变量：

#### 方法1: 通过 Vercel Dashboard
1. 访问 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择您的项目
3. 进入 Settings > Environment Variables
4. 添加所需的环境变量

#### 方法2: 通过 CLI
```bash
vercel env add AI_API_KEY
vercel env add FEISHU_WEBHOOK_URL
vercel env add FEISHU_WEBHOOK_SECRET
```

## 🔧 项目结构

```
AI_daily/
├── index.html          # 前端页面
├── api/                 # Serverless Functions
│   ├── run-scraper.py   # 主要API端点
│   ├── health.py        # 健康检查
│   └── requirements.txt # Python依赖
├── src/                 # 核心业务逻辑
├── vercel.json          # Vercel配置
└── config.yaml          # 应用配置
```

## 🌐 使用方法

部署成功后：
1. 访问您的 Vercel 域名 (例如: https://your-project.vercel.app)
2. 点击 "🚀 生成今日AI日报" 按钮
3. 等待1-2分钟，系统会自动生成日报并推送到飞书

## 🔍 常见问题

### Q: 部署失败怎么办？
A: 检查以下项目：
- 确保所有环境变量都已正确设置
- 检查 API 密钥是否有效
- 查看 Vercel 部署日志了解具体错误

### Q: 按钮点击后没有反应？
A: 
- 检查浏览器开发者工具的控制台是否有错误
- 确认环境变量配置正确
- 访问 `/api/health` 检查服务状态

### Q: 生成时间过长？
A: Serverless Function 在 Vercel 上有执行时间限制：
- 免费版: 10秒
- Pro版: 60秒
- 如需更长时间，考虑优化代码或升级套餐

### Q: 如何查看日志？
A: 在 Vercel Dashboard 中：
1. 进入您的项目
2. 点击 "Functions" 标签
3. 查看相关函数的日志

## 🚀 高级配置

### 自定义域名
在 Vercel Dashboard 的 Domains 设置中可以添加自定义域名。

### 定时任务
Vercel 本身不支持定时任务，如需定时执行，可以：
1. 使用外部 cron 服务（如 GitHub Actions）
2. 使用 Vercel Cron (Beta)
3. 集成第三方服务如 Zapier

## 📝 注意事项

1. **执行时间限制**: Vercel 有函数执行时间限制，请确保任务能在限制时间内完成
2. **文件系统**: Serverless 环境的文件系统是只读的，报告文件会保存到临时目录
3. **冷启动**: 首次调用可能需要较长时间，这是正常的冷启动现象
4. **内存限制**: 注意 Serverless Function 的内存使用量
5. **费用**: 虽然 Vercel 有免费额度，但大量使用可能产生费用

## 🎯 性能优化建议

1. **减少依赖**: 只安装必要的 Python 包
2. **缓存策略**: 考虑缓存频繁访问的数据
3. **异步处理**: 对于耗时操作，考虑异步处理
4. **错误处理**: 完善错误处理机制，避免函数崩溃

## 📞 技术支持

如果遇到问题，请：
1. 查看本文档的常见问题部分
2. 检查 Vercel 官方文档
3. 查看项目的 GitHub Issues

---

🌈 祝您部署成功！享受自动化的 AI 日报服务！ 