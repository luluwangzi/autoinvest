"""
强烈推荐页面 - 批量分析
自动分析纳斯达克100成分股，批量筛选高质量期权机会
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os
import time

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from options_calculator import calculator
from data_fetcher import data_fetcher


def main():
    st.set_page_config(
        page_title="强烈推荐",
        page_icon="⭐",
        layout="wide"
    )
    
    st.title("⭐ 强烈推荐 - 批量期权分析")
    st.markdown("---")
    
    # 侧边栏参数设置
    with st.sidebar:
        st.header("🔧 分析参数")
        
        # 股票数量选择
        max_stocks = st.slider(
            "分析股票数量",
            min_value=5,
            max_value=20,
            value=10,
            help="选择要分析的纳斯达克100成分股数量（建议不超过20以避免API限制）"
        )
        
        # 筛选条件
        st.subheader("📋 筛选条件")
        
        min_annual_return = st.slider(
            "最小年化收益率 (%)",
            min_value=10,
            max_value=100,
            value=25,
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
            max_value=500,
            value=50,
            help="只显示成交量大于此值的期权"
        )
        
        max_dte = st.slider(
            "最大到期天数",
            min_value=1,
            max_value=45,
            value=30,
            help="只显示到期天数小于此值的期权"
        )
        
        # 分析按钮
        analyze_button = st.button("🚀 开始批量分析", type="primary")
    
    # 主内容区域
    if analyze_button:
        # 显示市场状态
        market_status = data_fetcher.get_market_status()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if market_status['is_market_open']:
                st.success("🟢 市场开放")
            else:
                st.warning("🔴 市场关闭")
        
        with col2:
            st.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        with col3:
            st.info(f"🎯 分析 {max_stocks} 只股票")
        
        st.markdown("---")
        
        # 创建进度条
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # 获取纳斯达克100成分股
        status_text.text("📋 获取纳斯达克100成分股...")
        nasdaq_symbols = data_fetcher.get_nasdaq100_symbols()
        selected_symbols = nasdaq_symbols[:max_stocks]
        
        # 显示API限制提示
        st.info("ℹ️ 由于Yahoo Finance API限制，部分数据可能使用模拟数据。建议减少分析股票数量以获得更好的体验。")
        
        progress_bar.progress(0.1)
        
        # 批量分析期权
        all_results = []
        total_stocks = len(selected_symbols)
        
        for i, symbol in enumerate(selected_symbols):
            try:
                status_text.text(f"📊 分析 {symbol} ({i+1}/{total_stocks})...")
                
                # 获取股票信息
                stock_info = data_fetcher.get_stock_info(symbol)
                
                if stock_info['current_price'] == 0:
                    continue
                
                # 获取期权链数据
                options_data = data_fetcher.get_options_chain(symbol)
                
                if 'puts' not in options_data or options_data['puts'].empty:
                    continue
                
                # 分析Put期权
                puts_df = options_data['puts'].copy()
                puts_df = data_fetcher.validate_option_data(puts_df, stock_info['current_price'])
                
                if puts_df.empty:
                    continue
                
                # 计算期权指标
                for _, option in puts_df.iterrows():
                    # 检查必要字段是否存在
                    if 'dte' not in option or pd.isna(option['dte']):
                        continue
                    
                    # 准备期权数据
                    option_data = {
                        'current_price': stock_info['current_price'],
                        'strike_price': option['strike_price'],
                        'dte': int(option['dte']),  # 确保是整数
                        'option_price': option['option_price'],
                        'option_type': 'put'
                    }
                    
                    # 计算分析指标
                    analysis = calculator.analyze_option(option_data)
                    
                    # 添加股票信息
                    analysis.update({
                        'symbol': symbol,
                        'stock_name': stock_info['name'],
                        'current_price': stock_info['current_price'],
                        'sector': stock_info['sector'],
                        'expiration_date': option.get('expiration_date', ''),
                        'volume': option.get('volume', 0),
                        'open_interest': option.get('open_interest', 0),
                        'bid_price': option.get('bid_price', 0),
                        'ask_price': option.get('ask_price', 0),
                        'dte': int(option['dte']),  # 确保dte字段被添加
                        'strike_price': option['strike_price']  # 确保strike_price字段被添加
                    })
                    
                    all_results.append(analysis)
                
                # 更新进度条
                progress = 0.1 + (i + 1) / total_stocks * 0.8
                progress_bar.progress(progress)
                
                # 添加延迟避免请求过于频繁
                time.sleep(0.3)
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        progress_bar.progress(1.0)
        status_text.text("✅ 分析完成！")
        
        if not all_results:
            st.warning("⚠️ 没有找到符合条件的期权")
            return
        
        # 转换为DataFrame
        results_df = pd.DataFrame(all_results)
        
        # 应用筛选条件
        filtered_df = results_df[
            (results_df['annualized_return'] >= min_annual_return) &
            (results_df['assignment_probability'] <= max_assignment_prob) &
            (results_df['volume'] >= min_volume) &
            (results_df['dte'] <= max_dte) &
            (results_df['strike_price'] < results_df['current_price'])  # 只显示价外期权
        ].copy()
        
        if filtered_df.empty:
            st.warning("⚠️ 没有符合筛选条件的期权")
            st.info("💡 建议调整筛选条件，如降低年化收益率要求")
            return
        
        # 按年化收益率排序
        filtered_df = filtered_df.sort_values('annualized_return', ascending=False)
        
        # 显示分析结果摘要
        st.subheader("📊 分析结果摘要")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("找到期权数量", len(filtered_df))
        
        with col2:
            avg_return = filtered_df['annualized_return'].mean()
            st.metric("平均年化收益率", f"{avg_return:.1%}")
        
        with col3:
            avg_risk = filtered_df['assignment_probability'].mean()
            st.metric("平均被指派概率", f"{avg_risk:.1%}")
        
        with col4:
            unique_stocks = filtered_df['symbol'].nunique()
            st.metric("涉及股票数量", unique_stocks)
        
        st.markdown("---")
        
        # 显示顶级推荐
        st.subheader("🏆 顶级推荐")
        
        top_options = filtered_df.head(10)
        
        for i, (_, option) in enumerate(top_options.iterrows()):
            with st.expander(f"🥇 推荐 #{i+1}: {option['symbol']} {option['strike_price']:.1f} PUT (年化收益: {option['annualized_return']:.1%})"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("股票", option['symbol'])
                    st.metric("当前价格", f"${option['current_price']:.2f}")
                    st.metric("行权价", f"${option['strike_price']:.1f}")
                
                with col2:
                    st.metric("年化收益率", f"{option['annualized_return']:.1%}")
                    st.metric("被指派概率", f"{option['assignment_probability']:.1%}")
                    st.metric("到期天数", f"{option['dte']} 天")
                
                with col3:
                    st.metric("期权价格", f"${option['option_price']:.2f}")
                    st.metric("盈亏平衡价", f"${option['breakeven_price']:.2f}")
                    st.metric("成交量", f"{option['volume']:,}")
                
                with col4:
                    st.metric("Delta", f"{option['delta']:.3f}")
                    st.metric("Gamma", f"{option['gamma']:.4f}")
                    st.metric("Theta", f"{option['theta']:.4f}")
                
                # 风险评级
                risk_score = option['assignment_probability'] * 100
                if risk_score < 20:
                    st.success("🟢 低风险")
                elif risk_score < 35:
                    st.warning("🟡 中等风险")
                else:
                    st.error("🔴 高风险")
        
        # 显示详细数据表
        st.subheader("📋 详细数据表")
        
        # 选择显示的列
        display_columns = [
            'symbol', 'strike_price', 'option_price', 'annualized_return', 
            'assignment_probability', 'dte', 'volume', 'current_price',
            'delta', 'breakeven_price', 'sector'
        ]
        
        display_df = filtered_df[display_columns].copy()
        display_df.columns = [
            '股票代码', '行权价', '期权价格', '年化收益率', '被指派概率', 
            '到期天数', '成交量', '当前价格', 'Delta', '盈亏平衡价', '行业'
        ]
        
        # 格式化数值
        display_df['年化收益率'] = display_df['年化收益率'].apply(lambda x: f"{x:.1%}")
        display_df['被指派概率'] = display_df['被指派概率'].apply(lambda x: f"{x:.1%}")
        display_df['期权价格'] = display_df['期权价格'].apply(lambda x: f"${x:.2f}")
        display_df['当前价格'] = display_df['当前价格'].apply(lambda x: f"${x:.2f}")
        display_df['盈亏平衡价'] = display_df['盈亏平衡价'].apply(lambda x: f"${x:.2f}")
        
        st.dataframe(display_df, use_container_width=True)
        
        # 可视化分析
        st.subheader("📈 可视化分析")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 年化收益率分布
            fig1 = px.histogram(
                filtered_df,
                x='annualized_return',
                title="年化收益率分布",
                labels={'annualized_return': '年化收益率', 'count': '数量'},
                nbins=20
            )
            fig1.update_layout(height=400)
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # 被指派概率分布
            fig2 = px.histogram(
                filtered_df,
                x='assignment_probability',
                title="被指派概率分布",
                labels={'assignment_probability': '被指派概率', 'count': '数量'},
                nbins=20
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, use_container_width=True)
        
        # 行业分析
        st.subheader("🏭 行业分析")
        
        sector_analysis = filtered_df.groupby('sector').agg({
            'annualized_return': ['mean', 'count'],
            'assignment_probability': 'mean'
        }).round(3)
        
        sector_analysis.columns = ['平均年化收益率', '期权数量', '平均被指派概率']
        sector_analysis = sector_analysis.sort_values('平均年化收益率', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.dataframe(sector_analysis, use_container_width=True)
        
        with col2:
            # 行业分布饼图
            sector_counts = filtered_df['sector'].value_counts()
            fig3 = px.pie(
                values=sector_counts.values,
                names=sector_counts.index,
                title="期权分布 - 按行业"
            )
            fig3.update_layout(height=400)
            st.plotly_chart(fig3, use_container_width=True)
        
        # 风险收益散点图
        st.subheader("⚖️ 风险收益分析")
        
        fig4 = px.scatter(
            filtered_df,
            x='assignment_probability',
            y='annualized_return',
            size='volume',
            color='dte',
            hover_data=['symbol', 'strike_price', 'option_price'],
            title="风险收益散点图",
            labels={
                'assignment_probability': '被指派概率',
                'annualized_return': '年化收益率',
                'dte': '到期天数',
                'volume': '成交量'
            }
        )
        fig4.update_layout(height=500)
        st.plotly_chart(fig4, use_container_width=True)
        
        # 导出功能
        st.subheader("💾 导出数据")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 下载CSV文件"):
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="下载数据",
                    data=csv,
                    file_name=f"options_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 生成报告"):
                st.info("📋 报告功能开发中...")
        
        # 风险提示
        st.info("""
        ⚠️ **重要风险提示**:
        - 批量分析结果仅供参考，不构成投资建议
        - 期权交易存在高风险，可能导致全部本金损失
        - 建议在充分了解风险的前提下进行交易
        - 市场条件变化可能影响期权价格和风险
        - 请根据自己的风险承受能力选择合适的策略
        """)
    
    else:
        # 页面说明
        st.info("👆 请点击左侧的'开始批量分析'按钮开始分析")
        
        with st.expander("ℹ️ 功能说明"):
            st.markdown("""
            ### 📖 批量分析功能
            
            **强烈推荐页面** 自动分析纳斯达克100成分股，批量筛选高质量的Sell Put期权机会。
            
            ### 🔍 分析流程
            
            1. **获取成分股**: 自动获取纳斯达克100成分股列表
            2. **批量分析**: 逐个分析每只股票的期权链
            3. **智能筛选**: 应用多重筛选条件找出优质期权
            4. **结果排序**: 按年化收益率排序显示推荐结果
            
            ### 📋 筛选条件
            
            - **最小年化收益率**: 25% (可调整)
            - **最大被指派概率**: 30% (可调整)
            - **最小成交量**: 50 (可调整)
            - **最大到期天数**: 30天 (可调整)
            
            ### 💡 使用建议
            
            1. 建议在市场开放时进行分析以获得最新数据
            2. 关注成交量较大的期权以确保流动性
            3. 平衡年化收益率和被指派概率
            4. 考虑行业分散化投资
            5. 定期更新分析结果
            """)


if __name__ == "__main__":
    main()
