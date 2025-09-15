#!/bin/bash

# 美股期权分析策略平台启动脚本

echo "🚀 启动美股期权分析策略平台..."
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python 3.9+"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
python3 -c "import streamlit, yfinance, pandas, numpy, scipy, plotly" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  依赖未完全安装，正在安装..."
    python3 -m pip install --user -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请手动运行: pip install -r requirements.txt"
        exit 1
    fi
fi

echo "✅ 依赖检查完成"
echo ""

# 启动应用
echo "🌐 启动Streamlit应用..."
echo "📍 应用地址: http://localhost:8501"
echo "⏹️  按 Ctrl+C 停止应用"
echo ""

python3 -m streamlit run app.py --server.port 8501
