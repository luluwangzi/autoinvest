#!/bin/bash

# Streamlit Cloud 快速部署脚本

echo "🚀 美股期权分析策略平台 - Streamlit Cloud 部署脚本"
echo "=================================================="
echo ""

# 检查Git状态
if [ ! -d ".git" ]; then
    echo "📦 初始化Git仓库..."
    git init
    git add .
    git commit -m "Initial commit: 美股期权分析策略平台"
    echo "✅ Git仓库初始化完成"
    echo ""
fi

# 检查是否有远程仓库
if ! git remote | grep -q origin; then
    echo "⚠️  未检测到GitHub远程仓库"
    echo ""
    echo "请按照以下步骤操作："
    echo "1. 在GitHub上创建新仓库: https://github.com/new"
    echo "2. 仓库名称建议: autoinvest 或 options-analyzer"
    echo "3. 设置为公开仓库（Streamlit Cloud需要）"
    echo "4. 不要初始化README、.gitignore或license"
    echo ""
    echo "创建完成后，运行以下命令："
    echo "git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
    echo "git branch -M main"
    echo "git push -u origin main"
    echo ""
    echo "然后访问 https://share.streamlit.io/ 进行部署"
    exit 1
fi

# 检查文件完整性
echo "🔍 检查部署文件..."
required_files=(
    "app.py"
    "streamlit_app.py"
    "options_calculator.py"
    "data_fetcher.py"
    "utils.py"
    "requirements.txt"
    "packages.txt"
    "pages/1_单股票期权分析.py"
    "pages/2_强烈推荐.py"
    "pages/3_Sell_Call策略.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    echo "❌ 缺少以下必要文件："
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 所有必要文件检查完成"
echo ""

# 提交更改
echo "📝 提交代码更改..."
git add .
git commit -m "Update: 准备Streamlit Cloud部署 $(date '+%Y-%m-%d %H:%M:%S')" || echo "没有新的更改需要提交"
echo ""

# 推送到GitHub
echo "⬆️  推送到GitHub..."
git push origin main
echo ""

# 显示部署信息
echo "🎉 代码已推送到GitHub！"
echo ""
echo "📋 下一步操作："
echo "1. 访问 https://share.streamlit.io/"
echo "2. 使用GitHub账号登录"
echo "3. 点击 'New app'"
echo "4. 选择你的仓库: $(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')"
echo "5. 设置部署参数："
echo "   - Repository: $(git remote get-url origin | sed 's/.*github.com[:/]\([^.]*\).*/\1/')"
echo "   - Branch: main"
echo "   - Main file path: streamlit_app.py"
echo "6. 点击 'Deploy!'"
echo ""
echo "⏱️  部署时间：约2-5分钟"
echo "🌐 部署完成后，您将获得一个公开的Web应用URL"
echo ""
echo "📊 应用功能："
echo "   - 单股票期权分析"
echo "   - 批量期权筛选"
echo "   - Sell Call策略分析"
echo ""
echo "⚠️  注意事项："
echo "   - 确保仓库为公开仓库"
echo "   - 首次部署可能需要较长时间"
echo "   - 如遇问题，请检查Streamlit Cloud日志"
echo ""
echo "🔗 部署完成后，您的美股期权分析策略平台将面向全球用户提供服务！"
