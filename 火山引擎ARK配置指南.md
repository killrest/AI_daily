# 火山引擎ARK API配置指南

## 🔑 获取API密钥

### 1. 登录火山引擎控制台
访问：https://console.volcengine.com/ark/region:ark+cn-beijing/apiKey

### 2. 创建API密钥
1. 点击"新建API Key"
2. 输入密钥名称（如：彩虹一号AI日报）
3. 选择权限范围：推理接口调用
4. 点击"确定"创建

### 3. 复制API密钥
⚠️ **重要：API密钥只会显示一次，请立即保存**

### 4. 配置到系统中

#### 方法一：修改.env文件（推荐）
```bash
# 在项目根目录的.env文件中添加：
VOLCENGINE_ARK_API_KEY=your-api-key-here

# 例如：
VOLCENGINE_ARK_API_KEY=ak-1234567890abcdef1234567890abcdef
```

#### 方法二：环境变量
```bash
export VOLCENGINE_ARK_API_KEY="your-api-key-here"
```

## 🧪 测试API连接

配置完成后，运行以下命令测试：

```bash
# 检查配置
python3 main.py --mode config

# 测试完整流程
python3 main.py --mode once
```

## 📊 预期结果

配置成功后，您应该看到：
- ✅ AI分析正常工作
- ✅ 正确识别AI相关产品
- ✅ 生成详细的产品分析报告
- ✅ 飞书推送包含完整的AI产品信息

## 🔧 故障排除

### 1. 401未授权错误
- 检查API密钥是否正确
- 确认密钥没有过期
- 验证权限范围包含推理接口调用

### 2. 配置未生效
- 重启应用程序
- 检查.env文件格式
- 确认环境变量设置正确

### 3. 模型调用失败
- 确认endpoint_id正确：`ep-m-20250413002708-ct9mc`
- 检查模型名称：`deepseek-v3`
- 验证网络连接

## 💡 当前状态

目前系统使用的配置：
- **AI提供商**: volcengine_ark  
- **AI模型**: deepseek-v3
- **ARK端点**: ep-m-20250413002708-ct9mc
- **API密钥**: 需要配置 ⚠️

## 📝 备注

- API密钥配置后会立即生效
- 支持热重载，无需重启系统
- 建议定期更换API密钥确保安全 