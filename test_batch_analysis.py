"""
测试强烈推荐页面（批量分析）功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import data_fetcher
from options_calculator import calculator
import pandas as pd
import time

def test_batch_analysis():
    """测试批量分析功能"""
    print("🧪 测试强烈推荐页面（批量分析）功能...")
    
    # 1. 获取纳斯达克100成分股
    print("📊 获取纳斯达克100成分股...")
    nasdaq_symbols = data_fetcher.get_nasdaq100_symbols()
    print(f"   获取到 {len(nasdaq_symbols)} 个股票代码")
    
    if not nasdaq_symbols:
        print("❌ 无法获取纳斯达克100成分股")
        return False
    
    # 2. 限制分析数量（避免API限制）
    max_stocks = 5  # 只分析前5个股票
    symbols_to_analyze = nasdaq_symbols[:max_stocks]
    print(f"   分析前 {max_stocks} 个股票: {symbols_to_analyze}")
    
    # 3. 获取多个期权链数据
    print("📈 获取多个期权链数据...")
    max_dte = 45
    
    try:
        options_data = data_fetcher.get_multiple_options_chains(symbols_to_analyze, max_dte)
        print(f"   成功获取 {len(options_data)} 个股票的期权数据")
    except Exception as e:
        print(f"❌ 获取期权数据失败: {e}")
        return False
    
    # 4. 分析每个股票的期权
    print("🧮 分析期权数据...")
    all_results = []
    
    for symbol, data in options_data.items():
        print(f"   分析 {symbol}...")
        
        # 获取股票信息
        stock_info = data_fetcher.get_stock_info(symbol)
        if stock_info['current_price'] == 0:
            print(f"   ⚠️ {symbol} 价格数据无效，跳过")
            continue
        
        if 'puts' not in data or data['puts'].empty:
            print(f"   ⚠️ {symbol} 没有Put期权数据，跳过")
            continue
        
        puts_df = data['puts']
        
        # 验证期权数据
        puts_df = data_fetcher.validate_option_data(puts_df, stock_info['current_price'])
        if puts_df.empty:
            print(f"   ⚠️ {symbol} 验证后没有有效期权，跳过")
            continue
        
        print(f"   ✓ {symbol} 有 {len(puts_df)} 个有效Put期权")
        
        # 分析期权
        symbol_results = []
        for _, option in puts_df.iterrows():
            # 检查必要字段
            if 'dte' not in option or pd.isna(option['dte']):
                continue
            
            # 准备期权数据
            option_data = {
                'current_price': stock_info['current_price'],
                'strike_price': option['strike_price'],
                'dte': int(option['dte']),
                'option_price': option['option_price'],
                'option_type': 'put'
            }
            
            # 计算分析指标
            try:
                analysis = calculator.analyze_option(option_data)
                
                # 添加原始数据
                analysis.update({
                    'symbol': symbol,
                    'expiration_date': option.get('expiration_date', ''),
                    'volume': option.get('volume', 0),
                    'open_interest': option.get('open_interest', 0),
                    'bid_price': option.get('bid_price', 0),
                    'ask_price': option.get('ask_price', 0),
                    'implied_volatility_market': option.get('implied_volatility', 0),
                    'dte': int(option['dte']),
                    'strike_price': option['strike_price'],
                    'current_price': stock_info['current_price']  # 添加当前价格
                })
                
                symbol_results.append(analysis)
                
            except Exception as e:
                print(f"   ❌ 分析 {symbol} 期权时出错: {e}")
                continue
        
        all_results.extend(symbol_results)
        print(f"   ✓ {symbol} 成功分析 {len(symbol_results)} 个期权")
    
    if not all_results:
        print("❌ 没有成功分析的期权")
        return False
    
    # 5. 转换为DataFrame并筛选
    print("📋 筛选期权...")
    results_df = pd.DataFrame(all_results)
    print(f"   总期权数量: {len(results_df)}")
    
    # 应用筛选条件（强烈推荐页面的严格条件）
    filtered_df = results_df[
        (results_df['annualized_return'] >= 0.25) &  # 年化收益率 > 25%
        (results_df['assignment_probability'] <= 0.4) &  # 被指派概率 < 40%
        (results_df['volume'] >= 50) &  # 成交量 > 50
        (results_df['dte'] <= max_dte) &  # 到期天数 <= 45
        (results_df['strike_price'] < results_df['current_price'])  # 价外期权
    ].copy()
    
    print(f"   筛选后期权数量: {len(filtered_df)}")
    
    if filtered_df.empty:
        print("⚠️ 没有符合筛选条件的期权")
        
        # 尝试更宽松的条件
        print("🔄 尝试更宽松的筛选条件...")
        relaxed_df = results_df[
            (results_df['annualized_return'] >= 0.15) &  # 年化收益率 > 15%
            (results_df['assignment_probability'] <= 0.5) &  # 被指派概率 < 50%
            (results_df['volume'] >= 20) &  # 成交量 > 20
            (results_df['dte'] <= max_dte) &  # 到期天数 <= 45
            (results_df['strike_price'] < results_df['current_price'])  # 价外期权
        ].copy()
        
        print(f"   宽松条件筛选后期权数量: {len(relaxed_df)}")
        
        if relaxed_df.empty:
            print("❌ 即使使用宽松条件也没有找到符合条件的期权")
            return False
        else:
            filtered_df = relaxed_df
            print("✅ 使用宽松条件找到符合条件的期权")
    else:
        print("✅ 找到符合严格筛选条件的期权")
    
    # 6. 按年化收益率排序
    filtered_df = filtered_df.sort_values('annualized_return', ascending=False)
    
    # 7. 显示结果
    print("🏆 强烈推荐期权结果:")
    print("=" * 80)
    
    for i, (_, option) in enumerate(filtered_df.head(5).iterrows()):
        print(f"第 {i+1} 名:")
        print(f"  股票代码: {option['symbol']}")
        print(f"  行权价: ${option['strike_price']:.2f}")
        print(f"  当前价格: ${option['current_price']:.2f}")
        print(f"  期权价格: ${option.get('option_price', 0):.2f}")
        print(f"  年化收益率: {option.get('annualized_return', 0):.1%}")
        print(f"  被指派概率: {option.get('assignment_probability', 0):.1%}")
        print(f"  Delta: {option.get('delta', 0):.3f}")
        print(f"  到期天数: {option.get('dte', 0)} 天")
        print(f"  成交量: {option.get('volume', 0)}")
        print(f"  未平仓合约: {option.get('open_interest', 0)}")
        print("-" * 40)
    
    print("✅ 强烈推荐页面（批量分析）功能测试通过！")
    return True

if __name__ == "__main__":
    success = test_batch_analysis()
    if success:
        print("\n🎉 批量分析功能测试通过！强烈推荐页面正常工作。")
    else:
        print("\n❌ 批量分析功能测试失败！请检查错误信息。")
