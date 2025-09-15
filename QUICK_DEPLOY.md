# 🚀 快速部署到 Streamlit Cloud

## 📋 部署步骤（5分钟完成）

### 1. 准备GitHub仓库
```bash
# 如果还没有GitHub仓库，先创建一个
# 访问 https://github.com/new
# 仓库名称：autoinvest 或 options-analyzer
# 设置为公开仓库
```

### 2. 上传代码到GitHub
```bash
# 运行部署脚本
./deploy_to_streamlit.sh

# 或者手动操作：
git init
git add .
git commit -m "Initial commit: 美股期权分析策略平台"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 3. 部署到Streamlit Cloud
1. 访问 https://share.streamlit.io/
2. 使用GitHub账号登录
3. 点击 "New app"
4. 填写部署信息：
   - **Repository**: yourusername/autoinvest
   - **Branch**: main
   - **Main file path**: streamlit_app.py
   - **App URL**: 自定义（可选）
5. 点击 "Deploy!"

### 4. 等待部署完成
- 部署时间：2-5分钟
- 查看部署日志确认无错误
- 获得公开访问URL

## ✅ 部署检查清单

- [ ] GitHub仓库已创建（公开）
- [ ] 代码已推送到GitHub
- [ ] Streamlit Cloud账号已登录
- [ ] 部署参数设置正确
- [ ] 应用成功启动
- [ ] 所有功能正常工作

## 🎯 部署后功能

部署成功后，您的应用将提供：

### 📊 单股票期权分析
- 输入股票代码分析Sell Put策略
- 实时计算年化收益率、被指派概率
- 智能推荐高收益低风险期权

### ⭐ 批量期权筛选
- 自动分析纳斯达克100成分股
- 批量发现优质期权机会
- 支持自定义筛选条件

### 📈 Sell Call策略分析
- 基于持仓成本计算真实收益率
- 适用于已有股票持仓的投资者
- 风险收益平衡分析

## 🔧 技术特性

- **实时数据**: Yahoo Finance API集成
- **科学计算**: Black-Scholes期权定价模型
- **智能筛选**: 多重条件自动筛选
- **可视化**: 交互式图表和数据分析
- **响应式**: 支持桌面和移动端访问

## ⚠️ 重要说明

1. **数据限制**: Yahoo Finance API有请求频率限制
2. **风险提示**: 期权交易存在高风险，仅供参考
3. **网络要求**: 需要稳定的网络连接
4. **浏览器**: 建议使用Chrome、Firefox等现代浏览器

## 🆘 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
- 仓库是否为公开仓库
- requirements.txt文件是否正确
- 主文件路径是否为streamlit_app.py

### Q: 数据获取失败？
A: 这是正常现象，Yahoo Finance API有频率限制，稍后重试即可

### Q: 如何更新应用？
A: 推送新代码到GitHub，Streamlit Cloud会自动重新部署

## 📞 技术支持

- Streamlit Cloud文档: https://docs.streamlit.io/streamlit-community-cloud
- GitHub Issues: 在项目仓库中提交问题
- 社区支持: Streamlit Discord社区

---

**🎉 部署完成后，您的美股期权分析策略平台将面向全球用户提供服务！**
