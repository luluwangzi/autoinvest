# 🚀 Streamlit Cloud 部署指南

## 📋 部署前准备

### 1. 确保项目文件完整
```
autoinvest/
├── app.py                    # 主应用文件
├── streamlit_app.py          # Streamlit Cloud 入口文件
├── options_calculator.py     # 期权计算模块
├── data_fetcher.py          # 数据获取模块
├── utils.py                 # 工具函数
├── requirements.txt         # Python依赖
├── packages.txt             # 系统依赖
├── README.md               # 项目文档
├── .streamlit/
│   ├── config.toml         # Streamlit配置
│   └── secrets.toml        # 敏感信息配置
└── pages/                  # 页面模块
    ├── 1_单股票期权分析.py
    ├── 2_强烈推荐.py
    └── 3_Sell_Call策略.py
```

### 2. 检查依赖文件
- ✅ `requirements.txt` - Python包依赖
- ✅ `packages.txt` - 系统级依赖
- ✅ `streamlit_app.py` - 部署入口文件

## 🌐 Streamlit Cloud 部署步骤

### 方法一：通过 GitHub 部署（推荐）

1. **创建 GitHub 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: 美股期权分析策略平台"
   git branch -M main
   git remote add origin https://github.com/yourusername/autoinvest.git
   git push -u origin main
   ```

2. **访问 Streamlit Cloud**
   - 打开 https://share.streamlit.io/
   - 使用 GitHub 账号登录

3. **部署应用**
   - 点击 "New app"
   - 选择你的 GitHub 仓库
   - 设置部署参数：
     - **Repository**: yourusername/autoinvest
     - **Branch**: main
     - **Main file path**: streamlit_app.py
     - **App URL**: 自定义URL（可选）

4. **等待部署完成**
   - 部署过程大约需要 2-5 分钟
   - 查看部署日志确认无错误

### 方法二：直接上传部署

1. **准备部署包**
   ```bash
   # 创建部署包
   zip -r autoinvest-deploy.zip . -x "*.git*" "*__pycache__*" "*.log"
   ```

2. **上传到 Streamlit Cloud**
   - 访问 https://share.streamlit.io/
   - 选择 "Upload app"
   - 上传 zip 文件

## ⚙️ 部署配置

### 环境变量设置
在 Streamlit Cloud 中设置以下环境变量（如需要）：

```bash
# 可选的环境变量
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### 资源配置
- **CPU**: 1 vCPU（默认）
- **内存**: 1 GB（默认）
- **存储**: 1 GB（默认）

## 🔧 部署后配置

### 1. 自定义域名（可选）
- 在 Streamlit Cloud 设置中配置自定义域名
- 需要域名所有权验证

### 2. 监控和日志
- 查看应用日志：Streamlit Cloud Dashboard
- 监控性能指标
- 设置告警通知

### 3. 自动更新
- 启用 GitHub 自动部署
- 每次 push 到 main 分支自动更新

## 🚨 常见问题解决

### 1. 部署失败
```bash
# 检查依赖版本兼容性
pip check

# 验证应用启动
streamlit run streamlit_app.py
```

### 2. 数据获取问题
- Yahoo Finance API 限制：添加重试机制
- 网络超时：增加超时时间设置
- 数据格式错误：添加数据验证

### 3. 性能优化
```python
# 在 app.py 中添加缓存
@st.cache_data
def get_stock_data(symbol):
    return data_fetcher.get_stock_info(symbol)
```

## 📊 部署后测试

### 1. 功能测试
- [ ] 主页加载正常
- [ ] 单股票分析功能
- [ ] 批量分析功能
- [ ] Sell Call 策略分析
- [ ] 数据可视化正常

### 2. 性能测试
- [ ] 页面加载速度 < 3秒
- [ ] 数据获取响应时间 < 10秒
- [ ] 并发用户支持

### 3. 兼容性测试
- [ ] Chrome 浏览器
- [ ] Firefox 浏览器
- [ ] Safari 浏览器
- [ ] 移动端访问

## 🔒 安全考虑

### 1. 数据安全
- 不存储用户敏感信息
- 所有数据实时获取
- 无数据库依赖

### 2. API 安全
- Yahoo Finance 公开 API
- 无 API 密钥要求
- 请求频率限制处理

### 3. 用户隐私
- 不收集用户数据
- 无用户注册要求
- 匿名访问支持

## 📈 监控和维护

### 1. 性能监控
- 响应时间监控
- 错误率统计
- 用户访问量

### 2. 定期维护
- 依赖包更新
- 安全补丁应用
- 功能优化

### 3. 备份策略
- 代码版本控制
- 配置文件备份
- 部署历史记录

## 🎯 部署成功标志

部署成功后，您将获得：
- ✅ 公开访问的 Web 应用 URL
- ✅ 自动 HTTPS 证书
- ✅ 全球 CDN 加速
- ✅ 自动扩展能力
- ✅ 99.9% 可用性保证

## 📞 技术支持

如果在部署过程中遇到问题：
1. 查看 Streamlit Cloud 文档
2. 检查 GitHub Issues
3. 联系 Streamlit 社区支持

---

**部署完成后，您的美股期权分析策略平台将面向全球用户提供服务！** 🌍
