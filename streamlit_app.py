import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import data_fetcher

# 页面配置
st.set_page_config(
    page_title="美股期权分析策略平台",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    color: #1f77b4;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.3rem;
    font-weight: bold;
    color: #2c3e50;
    margin-top: 1.5rem;
    margin-bottom: 1rem;
}
.feature-card {
    background-color: #f8f9fa;
    padding: 1.2rem;
    border-radius: 8px;
    border-left: 4px solid #1f77b4;
    margin-bottom: 1rem;
}
.metric-card {
    background-color: #ffffff;
    padding: 0.8rem;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    text-align: center;
}
.warning-box {
    background-color: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
}
.info-box {
    background-color: #d1ecf1;
    border: 1px solid #bee5eb;
    border-radius: 6px;
    padding: 1rem;
    margin: 1rem 0;
}
/* 响应式设计 */
@media (max-width: 768px) {
    .main-header {
        font-size: 2rem;
    }
    .sub-header {
        font-size: 1.1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">📊 美股期权分析策略平台</h1>', unsafe_allow_html=True)

# 副标题
st.markdown("""
<div style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 3rem;">
    专业的Sell Put和Sell Call期权策略分析工具<br>
    基于Black-Scholes模型，实时数据驱动，智能推荐高收益低风险期权
</div>
""", unsafe_allow_html=True)

# 市场状态显示
st.markdown('<h2 class="sub-header">📈 市场状态</h2>', unsafe_allow_html=True)

try:
    market_status = data_fetcher.get_market_status()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if market_status['is_market_open']:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #28a745;">🟢 市场开放</h3>
                <p>实时数据更新中</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="metric-card">
                <h3 style="color: #dc3545;">🔴 市场关闭</h3>
                <p>使用历史数据</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📅 当前时间</h3>
            <p>{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 分析范围</h3>
            <p>纳斯达克100成分股</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ 更新频率</h3>
            <p>实时更新</p>
        </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.warning(f"⚠️ 无法获取市场状态: {str(e)}")

st.markdown("---")

# 功能模块介绍
st.markdown('<h2 class="sub-header">🚀 核心功能</h2>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 单股票期权分析</h3>
        <p><strong>功能:</strong> 分析指定股票的Sell Put策略</p>
        <p><strong>特点:</strong> 实时获取期权链数据，计算关键指标</p>
        <p><strong>适用:</strong> 寻找特定股票的高收益期权机会</p>
        <p><strong>筛选条件:</strong> 年化收益率>15%，被指派概率<40%</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>⭐ 强烈推荐</h3>
        <p><strong>功能:</strong> 批量分析纳斯达克100成分股</p>
        <p><strong>特点:</strong> 自动筛选高质量期权机会</p>
        <p><strong>适用:</strong> 快速发现市场中的优质期权</p>
        <p><strong>筛选条件:</strong> 年化收益率>25%，被指派概率<30%</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📈 Sell Call策略</h3>
        <p><strong>功能:</strong> 分析看涨期权卖出策略</p>
        <p><strong>特点:</strong> 基于持仓成本计算真实收益率</p>
        <p><strong>适用:</strong> 已有股票持仓的投资者</p>
        <p><strong>筛选条件:</strong> 年化收益率>15%，被指派概率<30%</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 技术特性
st.markdown('<h2 class="sub-header">🔧 技术特性</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="info-box">
        <h4>📊 数据质量保证</h4>
        <ul>
            <li><strong>历史数据回退:</strong> 非交易时段使用上一交易日数据</li>
            <li><strong>IV数据修复:</strong> 异常隐含波动率使用历史波动率</li>
            <li><strong>价格数据验证:</strong> 多重验证确保数据准确性</li>
            <li><strong>流动性筛选:</strong> 自动过滤低成交量期权</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-box">
        <h4>🧮 核心计算逻辑</h4>
        <ul>
            <li><strong>Black-Scholes模型:</strong> 期权定价和Greeks计算</li>
            <li><strong>年化收益率:</strong> (期权价格/行权价) × (365/DTE)</li>
            <li><strong>被指派概率:</strong> N(-d2) 基于BS模型</li>
            <li><strong>风险收益比:</strong> 最大盈利/最大亏损</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# 使用示例
st.markdown('<h2 class="sub-header">💡 使用示例</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h4>🎯 场景1: 寻找高收益期权</h4>
        <p><strong>操作:</strong> 在单股票分析页面输入AAPL</p>
        <p><strong>结果:</strong> 找到232.5 PUT，年化收益率114.1%，被指派概率28%</p>
        <p><strong>适用:</strong> 风险偏好较低的投资者</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h4>🚀 场景2: 批量发现机会</h4>
        <p><strong>操作:</strong> 在强烈推荐页面开始批量分析</p>
        <p><strong>结果:</strong> 自动筛选符合条件的高质量期权</p>
        <p><strong>适用:</strong> 专业投资者快速扫描市场</p>
    </div>
    """, unsafe_allow_html=True)

# 风险提示
st.markdown('<h2 class="sub-header">⚠️ 重要风险提示</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="warning-box">
    <h4>🚨 期权交易风险警告</h4>
    <ul>
        <li><strong>高风险投资:</strong> 期权交易存在高风险，可能导致全部本金损失</li>
        <li><strong>模型局限性:</strong> Black-Scholes模型基于理论假设，实际结果可能不同</li>
        <li><strong>市场波动:</strong> 市场条件变化可能影响期权价格和风险</li>
        <li><strong>流动性风险:</strong> 某些期权可能缺乏足够的流动性</li>
        <li><strong>时间衰减:</strong> 期权价值会随时间衰减，需要及时管理</li>
    </ul>
    <p><strong>免责声明:</strong> 本平台提供的分析结果仅供参考，不构成投资建议。投资者应根据自身情况谨慎决策。</p>
</div>
""", unsafe_allow_html=True)

# 快速开始
st.markdown('<h2 class="sub-header">🚀 快速开始</h2>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h4>📋 使用步骤</h4>
    <ol>
        <li><strong>选择功能:</strong> 从左侧导航栏选择需要的分析功能</li>
        <li><strong>设置参数:</strong> 在侧边栏调整筛选条件和分析参数</li>
        <li><strong>开始分析:</strong> 点击"开始分析"按钮获取结果</li>
        <li><strong>查看结果:</strong> 分析推荐期权和详细数据</li>
        <li><strong>风险评估:</strong> 仔细评估风险后做出投资决策</li>
    </ol>
</div>
""", unsafe_allow_html=True)

# 页脚
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>📊 美股期权分析策略平台 | 基于Streamlit构建 | 数据来源: Yahoo Finance</p>
    <p>⚠️ 投资有风险，入市需谨慎 | 本平台仅供参考，不构成投资建议</p>
</div>
""", unsafe_allow_html=True)
