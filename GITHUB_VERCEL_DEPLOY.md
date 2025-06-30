# 🌈 彩虹一号 AI 日报 - GitHub + Vercel 部署指南

## 🚀 快速部署步骤

### 第一步：准备GitHub仓库

1. **创建GitHub仓库**
   - 访问 [GitHub](https://github.com) 并登录
   - 点击右上角的 "+" → "New repository"
   - 仓库名称：`ai-daily-report` (或您喜欢的名称)
   - 设为 Public 或 Private (都可以)
   - 点击 "Create repository"

2. **上传项目代码**
   ```bash
   # 在项目根目录执行
   git init
   git add .
   git commit -m "🌈 初始化彩虹一号AI日报系统"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

### 第二步：连接Vercel

1. **访问Vercel**
   - 打开 [vercel.com](https://vercel.com)
   - 使用GitHub账号登录

2. **导入项目**
   - 点击 "Add New..." → "Project"
   - 在GitHub仓库列表中找到您的项目
   - 点击 "Import"

3. **项目配置**
   - Project Name: 保持默认或自定义
   - Framework Preset: 选择 "Other"
   - Root Directory: 保持默认 "./"
   - 点击 "Deploy"

### 第三步：配置环境变量

在Vercel Dashboard中：

1. **进入项目设置**
   - 项目部署完成后，点击项目名称
   - 点击顶部的 "Settings" 标签
   - 在左侧菜单点击 "Environment Variables"

2. **添加必需的环境变量**
   
   **AI服务配置**：
   ```
   变量名: AI_API_KEY
   值: 您的火山引擎ARK平台API密钥
   ```

   **飞书机器人配置**：
   ```
   变量名: FEISHU_WEBHOOK_URL
   值: https://open.feishu.cn/open-apis/bot/v2/hook/YOUR_WEBHOOK_ID
   
   变量名: FEISHU_WEBHOOK_SECRET
   值: 您的飞书机器人签名密钥
   ```

3. **保存配置**
   - 添加完所有环境变量后
   - Vercel会自动触发重新部署

### 第四步：测试部署

1. **访问您的网站**
   - 部署完成后，Vercel会提供一个域名
   - 访问 `https://your-project-name.vercel.app`

2. **测试功能**
   - 点击 "🚀 生成今日AI日报" 按钮
   - 等待1-2分钟，观察状态反馈
   - 检查飞书群是否收到日报

## 🔧 项目特点

- ✅ 自动识别并排除敏感信息
- ✅ 无需本地环境，完全cloud-native
- ✅ 支持自动部署（push代码自动更新）
- ✅ 免费套餐足够日常使用

## 📝 环境变量详解

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `AI_API_KEY` | ✅ | 火山引擎ARK平台API密钥 |
| `FEISHU_WEBHOOK_URL` | ✅ | 飞书机器人Webhook地址 |
| `FEISHU_WEBHOOK_SECRET` | ✅ | 飞书机器人签名密钥 |

## 🎯 常见问题

### Q: 部署后点击按钮没反应？
**A**: 检查环境变量是否正确配置，特别是API密钥。

### Q: 飞书收不到消息？
**A**: 
1. 确认Webhook URL和密钥正确
2. 确认机器人已添加到目标群聊
3. 检查飞书机器人权限设置

### Q: 如何查看错误日志？
**A**: 在Vercel Dashboard → 项目 → Functions → 查看相关函数日志

### Q: 如何更新代码？
**A**: 直接push到GitHub，Vercel会自动重新部署：
```bash
git add .
git commit -m "更新功能"
git push
```

### Q: 可以自定义域名吗？
**A**: 可以！在Vercel项目设置的Domains部分添加您的域名。

## 🌟 高级配置

### 自动部署
- 每次push到main分支，Vercel自动重新部署
- 支持预览部署（pull request）

### 团队协作
- 可以邀请团队成员到Vercel项目
- 支持不同环境的环境变量配置

### 监控和分析
- Vercel自带性能监控
- 可查看函数执行时间和错误率

## 🎉 部署完成！

恭喜！您的彩虹一号AI日报系统已成功部署到Vercel！

- 🌐 网站地址：`https://your-project-name.vercel.app`
- 🔄 自动更新：push代码即可更新
- 📱 响应式设计：支持手机、平板、电脑
- ⚡ 高性能：全球CDN加速

享受您的自动化AI日报服务吧！🌈 