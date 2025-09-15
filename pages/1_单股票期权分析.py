"""
单股票期权分析页面
分析指定股票的Sell Put策略，推荐高收益低风险期权
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from options_calculator import calculator
from data_fetcher import data_fetcher


def main():
    st.set_page_config(
        page_title="单股票期权分析",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 单股票期权分析")
    st.markdown("---")
    
    # 侧边栏输入
    with st.sidebar:
        st.header("🔧 分析参数")
        
        # 股票代码输入
        symbol = st.text_input(
            "股票代码",
            value="AAPL",
            help="输入美股股票代码，如AAPL、TSLA等",
            placeholder="AAPL"
        ).upper()
        
        # 筛选条件
        st.subheader("📋 筛选条件")
        
        min_annual_return = st.slider(
            "最小年化收益率 (%)",
            min_value=5,
            max_value=50,
            value=15,
            help="只显示年化收益率大于此值的期权"
        ) / 100
        
        max_assignment_prob = st.slider(
            "最大被指派概率 (%)",
            min_value=10,
            max_value=80,
            value=40,
            help="只显示被指派概率小于此值的期权"
        ) / 100
        
        min_volume = st.number_input(
            "最小成交量",
            min_value=1,
            max_value=1000,
            value=50,
            help="只显示成交量大于此值的期权"
        )
        
        max_dte = st.slider(
            "最大到期天数",
            min_value=1,
            max_value=60,
            value=45,
            help="只显示到期天数小于此值的期权"
        )
        
        # 分析按钮
        analyze_button = st.button("🚀 开始分析", type="primary")
    
    # 主内容区域
    if analyze_button and symbol:
        with st.spinner(f"正在分析 {symbol} 的期权数据..."):
            try:
                # 获取股票信息
                stock_info = data_fetcher.get_stock_info(symbol)
                
                if stock_info['current_price'] == 0:
                    st.error(f"❌ 无法获取 {symbol} 的股票数据，请检查股票代码是否正确")
                    return
                
                # 显示股票基本信息
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "当前价格",
                        f"${stock_info['current_price']:.2f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "历史波动率",
                        f"{stock_info['historical_volatility']:.1%}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "市值",
                        f"${stock_info['market_cap']/1e9:.1f}B" if stock_info['market_cap'] > 0 else "N/A",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        "行业",
                        stock_info['sector'],
                        delta=None
                    )
                
                st.markdown("---")
                
                # 获取期权链数据
                options_data = data_fetcher.get_options_chain(symbol)
                
                if options_data['puts'].empty:
                    st.warning(f"⚠️ 未找到 {symbol} 的Put期权数据")
                    return
                
                # 分析Put期权
                puts_df = options_data['puts'].copy()
                puts_df = data_fetcher.validate_option_data(puts_df, stock_info['current_price'])
                
                if puts_df.empty:
                    st.warning("⚠️ 没有符合基本条件的Put期权")
                    return
                
                # 计算期权指标
                analysis_results = []
                
                for _, option in puts_df.iterrows():
                    # 准备期权数据
                    option_data = {
                        'current_price': stock_info['current_price'],
                        'strike_price': option['strike_price'],
                        'dte': option['dte'],
                        'option_price': option['option_price'],
                        'option_type': 'put'
                    }
                    
                    # 计算分析指标
                    analysis = calculator.analyze_option(option_data)
                    
                    # 添加原始数据
                    analysis.update({
                        'symbol': symbol,
                        'expiration_date': option['expiration_date'],
                        'volume': option['volume'],
                        'open_interest': option['open_interest'],
                        'bid_price': option['bid_price'],
                        'ask_price': option['ask_price'],
                        'implied_volatility_market': option.get('implied_volatility', 0)
                    })
                    
                    analysis_results.append(analysis)
                
                # 转换为DataFrame
                results_df = pd.DataFrame(analysis_results)
                
                # 应用筛选条件
                filtered_df = results_df[
                    (results_df['annualized_return'] >= min_annual_return) &
                    (results_df['assignment_probability'] <= max_assignment_prob) &
                    (results_df['volume'] >= min_volume) &
                    (results_df['dte'] <= max_dte) &
                    (results_df['strike_price'] < stock_info['current_price'])  # 只显示价外期权
                ].copy()
                
                if filtered_df.empty:
                    st.warning("⚠️ 没有符合筛选条件的期权")
                    st.info("💡 建议调整筛选条件，如降低年化收益率要求或增加被指派概率限制")
                    return
                
                # 按年化收益率排序
                filtered_df = filtered_df.sort_values('annualized_return', ascending=False)
                
                # 显示推荐结果
                st.subheader("🎯 推荐期权")
                
                # 显示前5个最佳期权
                top_options = filtered_df.head(5)
                
                for i, (_, option) in enumerate(top_options.iterrows()):
                    with st.expander(f"🥇 推荐 #{i+1}: {option['strike_price']:.1f} PUT (年化收益: {option['annualized_return']:.1%})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("年化收益率", f"{option['annualized_return']:.1%}")
                            st.metric("被指派概率", f"{option['assignment_probability']:.1%}")
                            st.metric("到期天数", f"{option['dte']} 天")
                        
                        with col2:
                            st.metric("期权价格", f"${option['option_price']:.2f}")
                            st.metric("盈亏平衡价", f"${option['breakeven_price']:.2f}")
                            st.metric("最大盈利", f"${option['max_profit']:.2f}")
                        
                        with col3:
                            st.metric("Delta", f"{option['delta']:.3f}")
                            st.metric("Gamma", f"{option['gamma']:.4f}")
                            st.metric("Theta", f"{option['theta']:.4f}")
                        
                        # 风险提示
                        if option['assignment_probability'] > 0.3:
                            st.warning("⚠️ 被指派概率较高，请注意风险")
                        if option['annualized_return'] > 1.0:
                            st.info("💡 年化收益率很高，请仔细评估风险")
                
                # 显示详细数据表
                st.subheader("📊 详细数据")
                
                # 选择显示的列
                display_columns = [
                    'strike_price', 'option_price', 'annualized_return', 
                    'assignment_probability', 'dte', 'volume', 'open_interest',
                    'delta', 'gamma', 'theta', 'breakeven_price'
                ]
                
                display_df = filtered_df[display_columns].copy()
                display_df.columns = [
                    '行权价', '期权价格', '年化收益率', '被指派概率', '到期天数',
                    '成交量', '持仓量', 'Delta', 'Gamma', 'Theta', '盈亏平衡价'
                ]
                
                # 格式化数值
                display_df['年化收益率'] = display_df['年化收益率'].apply(lambda x: f"{x:.1%}")
                display_df['被指派概率'] = display_df['被指派概率'].apply(lambda x: f"{x:.1%}")
                display_df['期权价格'] = display_df['期权价格'].apply(lambda x: f"${x:.2f}")
                display_df['盈亏平衡价'] = display_df['盈亏平衡价'].apply(lambda x: f"${x:.2f}")
                
                st.dataframe(display_df, use_container_width=True)
                
                # 可视化分析
                st.subheader("📈 可视化分析")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 年化收益率 vs 被指派概率散点图
                    fig1 = px.scatter(
                        filtered_df,
                        x='assignment_probability',
                        y='annualized_return',
                        size='volume',
                        color='dte',
                        hover_data=['strike_price', 'option_price'],
                        title="年化收益率 vs 被指派概率",
                        labels={
                            'assignment_probability': '被指派概率',
                            'annualized_return': '年化收益率',
                            'dte': '到期天数',
                            'volume': '成交量'
                        }
                    )
                    fig1.update_layout(height=400)
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # 行权价分布
                    fig2 = px.histogram(
                        filtered_df,
                        x='strike_price',
                        title="行权价分布",
                        labels={'strike_price': '行权价', 'count': '数量'}
                    )
                    fig2.update_layout(height=400)
                    st.plotly_chart(fig2, use_container_width=True)
                
                # 风险收益分析
                st.subheader("⚖️ 风险收益分析")
                
                # 计算风险收益比
                filtered_df['risk_reward_ratio'] = filtered_df['max_profit'] / filtered_df['max_loss']
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_return = filtered_df['annualized_return'].mean()
                    st.metric("平均年化收益率", f"{avg_return:.1%}")
                
                with col2:
                    avg_risk = filtered_df['assignment_probability'].mean()
                    st.metric("平均被指派概率", f"{avg_risk:.1%}")
                
                with col3:
                    avg_ratio = filtered_df['risk_reward_ratio'].mean()
                    st.metric("平均风险收益比", f"{avg_ratio:.2f}")
                
                # 风险提示
                st.info("""
                ⚠️ **风险提示**:
                - 期权交易存在高风险，可能导致全部本金损失
                - 被指派概率基于Black-Scholes模型计算，实际结果可能不同
                - 建议在充分了解风险的前提下进行交易
                - 本分析仅供参考，不构成投资建议
                """)
                
            except Exception as e:
                st.error(f"❌ 分析过程中出现错误: {str(e)}")
                st.info("💡 请检查网络连接或稍后重试")
    
    elif not symbol:
        st.info("👆 请在左侧输入股票代码开始分析")
    
    # 页面说明
    with st.expander("ℹ️ 使用说明"):
        st.markdown("""
        ### 📖 功能说明
        
        **单股票期权分析** 帮助您分析指定股票的Sell Put策略，找到高收益、低风险的期权交易机会。
        
        ### 🔍 分析指标
        
        - **年化收益率**: 基于期权价格和到期时间计算的年化收益
        - **被指派概率**: 期权到期时被指派的可能性
        - **Delta**: 期权价格对股价变化的敏感度
        - **Gamma**: Delta对股价变化的敏感度
        - **Theta**: 期权价格随时间衰减的速度
        - **盈亏平衡价**: 期权交易的盈亏平衡点
        
        ### 📋 筛选条件
        
        - **最小年化收益率**: 只显示收益率大于此值的期权
        - **最大被指派概率**: 只显示风险小于此值的期权
        - **最小成交量**: 确保期权有足够的流动性
        - **最大到期天数**: 控制期权的时间范围
        
        ### 💡 使用建议
        
        1. 选择流动性好的大盘股进行分析
        2. 关注年化收益率和被指派概率的平衡
        3. 优先选择成交量较大的期权
        4. 考虑自己的风险承受能力
        """)


if __name__ == "__main__":
    main()
