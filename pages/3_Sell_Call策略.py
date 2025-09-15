"""
Sell Call策略分析页面
分析看涨期权卖出策略，基于持仓成本计算年化收益率
适用于已有股票持仓的投资者
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
        page_title="Sell Call策略",
        page_icon="📈",
        layout="wide"
    )
    
    st.title("📈 Sell Call策略分析")
    st.markdown("---")
    
    # 侧边栏参数设置
    with st.sidebar:
        st.header("🔧 分析参数")
        
        # 股票代码输入
        symbol = st.text_input(
            "股票代码",
            value="AAPL",
            help="输入您已持有的股票代码",
            placeholder="AAPL"
        ).upper()
        
        # 持仓信息
        st.subheader("💼 持仓信息")
        
        shares_owned = st.number_input(
            "持有股数",
            min_value=1,
            max_value=10000,
            value=100,
            help="您持有的股票数量"
        )
        
        cost_basis = st.number_input(
            "持仓成本 ($)",
            min_value=0.01,
            max_value=10000.0,
            value=150.0,
            help="每股的买入成本"
        )
        
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
            max_value=60,
            value=30,
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
        with st.spinner(f"正在分析 {symbol} 的Sell Call策略..."):
            try:
                # 获取股票信息
                stock_info = data_fetcher.get_stock_info(symbol)
                
                if stock_info['current_price'] == 0:
                    st.error(f"❌ 无法获取 {symbol} 的股票数据，请检查股票代码是否正确")
                    return
                
                current_price = stock_info['current_price']
                
                # 计算持仓信息
                total_cost = shares_owned * cost_basis
                current_value = shares_owned * current_price
                unrealized_pnl = current_value - total_cost
                unrealized_pnl_pct = unrealized_pnl / total_cost
                
                # 显示持仓信息
                st.subheader("💼 当前持仓信息")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric(
                        "当前价格",
                        f"${current_price:.2f}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "持仓成本",
                        f"${cost_basis:.2f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        "未实现盈亏",
                        f"${unrealized_pnl:.2f}",
                        delta=f"{unrealized_pnl_pct:.1%}"
                    )
                
                with col4:
                    st.metric(
                        "持仓价值",
                        f"${current_value:.2f}",
                        delta=None
                    )
                
                st.markdown("---")
                
                # 获取期权链数据
                options_data = data_fetcher.get_options_chain(symbol)
                
                if options_data['calls'].empty:
                    st.warning(f"⚠️ 未找到 {symbol} 的Call期权数据")
                    return
                
                # 分析Call期权
                calls_df = options_data['calls'].copy()
                calls_df = data_fetcher.validate_option_data(calls_df, current_price)
                
                if calls_df.empty:
                    st.warning("⚠️ 没有符合基本条件的Call期权")
                    return
                
                # 计算期权指标
                analysis_results = []
                
                for _, option in calls_df.iterrows():
                    # 准备期权数据
                    option_data = {
                        'current_price': current_price,
                        'strike_price': option['strike_price'],
                        'dte': option['dte'],
                        'option_price': option['option_price'],
                        'option_type': 'call'
                    }
                    
                    # 计算分析指标
                    analysis = calculator.analyze_option(option_data)
                    
                    # 计算基于持仓成本的年化收益率
                    if option['strike_price'] > current_price:  # 只分析价外期权
                        # 如果被指派，收益 = 期权价格 + (行权价 - 持仓成本)
                        if_assigned_profit = option['option_price'] + (option['strike_price'] - cost_basis)
                        if_assigned_return = if_assigned_profit / cost_basis
                        
                        # 如果未被指派，收益 = 期权价格
                        if_not_assigned_profit = option['option_price']
                        if_not_assigned_return = if_not_assigned_profit / cost_basis
                        
                        # 期望收益 = 被指派概率 × 被指派收益 + (1-被指派概率) × 未被指派收益
                        expected_profit = (analysis['assignment_probability'] * if_assigned_profit + 
                                         (1 - analysis['assignment_probability']) * if_not_assigned_profit)
                        expected_return = expected_profit / cost_basis
                        
                        # 年化期望收益率
                        annualized_expected_return = expected_return * (365 / option['dte'])
                        
                        # 更新年化收益率
                        analysis['annualized_return'] = annualized_expected_return
                        analysis['expected_profit'] = expected_profit
                        analysis['if_assigned_return'] = if_assigned_return
                        analysis['if_not_assigned_return'] = if_not_assigned_return
                    
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
                    (results_df['strike_price'] > current_price)  # 只显示价外期权
                ].copy()
                
                if filtered_df.empty:
                    st.warning("⚠️ 没有符合筛选条件的期权")
                    st.info("💡 建议调整筛选条件，如降低年化收益率要求")
                    return
                
                # 按年化收益率排序
                filtered_df = filtered_df.sort_values('annualized_return', ascending=False)
                
                # 显示推荐结果
                st.subheader("🎯 推荐Call期权")
                
                # 显示前5个最佳期权
                top_options = filtered_df.head(5)
                
                for i, (_, option) in enumerate(top_options.iterrows()):
                    with st.expander(f"🥇 推荐 #{i+1}: {option['strike_price']:.1f} CALL (年化收益: {option['annualized_return']:.1%})"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("年化收益率", f"{option['annualized_return']:.1%}")
                            st.metric("被指派概率", f"{option['assignment_probability']:.1%}")
                            st.metric("到期天数", f"{option['dte']} 天")
                        
                        with col2:
                            st.metric("期权价格", f"${option['option_price']:.2f}")
                            st.metric("期望收益", f"${option['expected_profit']:.2f}")
                            st.metric("行权价", f"${option['strike_price']:.1f}")
                        
                        with col3:
                            st.metric("Delta", f"{option['delta']:.3f}")
                            st.metric("Gamma", f"{option['gamma']:.4f}")
                            st.metric("Theta", f"{option['theta']:.4f}")
                        
                        # 收益分析
                        st.subheader("💰 收益分析")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(
                                "被指派时收益",
                                f"${option['if_assigned_return'] * cost_basis:.2f}",
                                delta=f"{option['if_assigned_return']:.1%}"
                            )
                        
                        with col2:
                            st.metric(
                                "未被指派时收益",
                                f"${option['if_not_assigned_return'] * cost_basis:.2f}",
                                delta=f"{option['if_not_assigned_return']:.1%}"
                            )
                        
                        # 风险提示
                        if option['assignment_probability'] > 0.3:
                            st.warning("⚠️ 被指派概率较高，可能失去股票持仓")
                        if option['strike_price'] < cost_basis * 1.1:
                            st.info("💡 行权价接近持仓成本，被指派后收益有限")
                
                # 显示详细数据表
                st.subheader("📊 详细数据")
                
                # 选择显示的列
                display_columns = [
                    'strike_price', 'option_price', 'annualized_return', 
                    'assignment_probability', 'dte', 'volume', 'open_interest',
                    'expected_profit', 'if_assigned_return', 'if_not_assigned_return',
                    'delta', 'breakeven_price'
                ]
                
                display_df = filtered_df[display_columns].copy()
                display_df.columns = [
                    '行权价', '期权价格', '年化收益率', '被指派概率', '到期天数',
                    '成交量', '持仓量', '期望收益', '被指派收益', '未被指派收益',
                    'Delta', '盈亏平衡价'
                ]
                
                # 格式化数值
                display_df['年化收益率'] = display_df['年化收益率'].apply(lambda x: f"{x:.1%}")
                display_df['被指派概率'] = display_df['被指派概率'].apply(lambda x: f"{x:.1%}")
                display_df['期权价格'] = display_df['期权价格'].apply(lambda x: f"${x:.2f}")
                display_df['期望收益'] = display_df['期望收益'].apply(lambda x: f"${x:.2f}")
                display_df['被指派收益'] = display_df['被指派收益'].apply(lambda x: f"{x:.1%}")
                display_df['未被指派收益'] = display_df['未被指派收益'].apply(lambda x: f"{x:.1%}")
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
                        hover_data=['strike_price', 'option_price', 'expected_profit'],
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
                
                # 收益分析
                st.subheader("💰 收益分析")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_return = filtered_df['annualized_return'].mean()
                    st.metric("平均年化收益率", f"{avg_return:.1%}")
                
                with col2:
                    avg_risk = filtered_df['assignment_probability'].mean()
                    st.metric("平均被指派概率", f"{avg_risk:.1%}")
                
                with col3:
                    avg_expected_profit = filtered_df['expected_profit'].mean()
                    st.metric("平均期望收益", f"${avg_expected_profit:.2f}")
                
                # 策略建议
                st.subheader("💡 策略建议")
                
                best_option = filtered_df.iloc[0]
                
                st.info(f"""
                **基于当前持仓的最佳策略建议**:
                
                - **推荐期权**: {best_option['strike_price']:.1f} CALL
                - **期权价格**: ${best_option['option_price']:.2f}
                - **年化收益率**: {best_option['annualized_return']:.1%}
                - **被指派概率**: {best_option['assignment_probability']:.1%}
                
                **策略说明**:
                - 如果股价上涨到行权价以上，您将以${best_option['strike_price']:.1f}的价格卖出股票
                - 如果股价未达到行权价，您将保留股票并获得期权费
                - 这种策略适合对股票长期看涨但希望获得额外收益的投资者
                """)
                
                # 风险提示
                st.warning("""
                ⚠️ **重要风险提示**:
                - Sell Call策略会限制股票的上涨收益
                - 如果被指派，您将失去股票持仓
                - 期权交易存在高风险，可能导致损失
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
        ### 📖 Sell Call策略说明
        
        **Sell Call策略** 适用于已有股票持仓的投资者，通过卖出看涨期权获得额外收益。
        
        ### 🔍 策略原理
        
        1. **持有股票**: 您已经持有某只股票
        2. **卖出Call期权**: 卖出看涨期权获得期权费
        3. **两种结果**:
           - 股价上涨到行权价以上：被指派，以行权价卖出股票
           - 股价未达到行权价：保留股票，获得期权费
        
        ### 📊 收益计算
        
        - **被指派时收益** = 期权费 + (行权价 - 持仓成本)
        - **未被指派时收益** = 期权费
        - **期望收益** = 被指派概率 × 被指派收益 + (1-被指派概率) × 未被指派收益
        
        ### 💡 适用场景
        
        - 对股票长期看涨但希望获得额外收益
        - 愿意在特定价格卖出股票
        - 希望降低持仓成本
        - 对股票涨幅预期有限
        
        ### ⚠️ 风险提示
        
        - 限制股票的上涨收益
        - 可能失去股票持仓
        - 需要承担期权交易风险
        - 市场波动可能影响策略效果
        """)


if __name__ == "__main__":
    main()
