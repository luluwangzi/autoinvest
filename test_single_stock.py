"""
测试单股票期权分析功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import data_fetcher
from options_calculator import calculator
import pandas as pd

def test_single_stock_analysis():
    """测试单股票分析功能"""
    print("🧪 测试单股票期权分析功能...")
    
    symbol = "AAPL"
    
    # 1. 获取股票信息
    print(f"📊 获取 {symbol} 股票信息...")
    stock_info = data_fetcher.get_stock_info(symbol)
    print(f"   股票名称: {stock_info['name']}")
    print(f"   当前价格: ${stock_info['current_price']:.2f}")
    print(f"   历史波动率: {stock_info['historical_volatility']:.1%}")
    
    if stock_info['current_price'] == 0:
        print("❌ 无法获取股票价格")
        return False
    
    # 2. 获取期权链数据
    print(f"📈 获取 {symbol} 期权链数据...")
    options_data = data_fetcher.get_options_chain(symbol)
    
    puts_df = options_data['puts']
    print(f"   Put期权数量: {len(puts_df)}")
    
    if puts_df.empty:
        print("❌ 没有Put期权数据")
        return False
    
    # 3. 验证期权数据
    print("🔍 验证期权数据...")
    puts_df = data_fetcher.validate_option_data(puts_df, stock_info['current_price'])
    print(f"   验证后Put期权数量: {len(puts_df)}")
    
    if puts_df.empty:
        print("❌ 验证后没有有效的Put期权")
        return False
    
    # 4. 检查必要字段
    print("✅ 检查必要字段...")
    required_fields = ['strike_price', 'option_price', 'dte', 'volume']
    for field in required_fields:
        if field in puts_df.columns:
            print(f"   ✓ {field} 字段存在")
        else:
            print(f"   ❌ {field} 字段缺失")
            return False
    
    # 5. 分析期权
    print("🧮 分析期权...")
    analysis_results = []
    
    for i, (_, option) in enumerate(puts_df.head(3).iterrows()):  # 只分析前3个期权
        print(f"   分析期权 {i+1}: 行权价 ${option['strike_price']:.1f}")
        
        # 检查必要字段
        if 'dte' not in option or pd.isna(option['dte']):
            print(f"   ❌ 期权 {i+1} 缺少dte字段")
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
                'dte': int(option['dte']),  # 确保dte字段被添加
                'strike_price': option['strike_price']  # 确保strike_price字段被添加
            })
            
            analysis_results.append(analysis)
            
            print(f"   ✓ 年化收益率: {analysis['annualized_return']:.1%}")
            print(f"   ✓ 被指派概率: {analysis['assignment_probability']:.1%}")
            print(f"   ✓ Delta: {analysis['delta']:.3f}")
            
        except Exception as e:
            print(f"   ❌ 分析期权 {i+1} 时出错: {e}")
            return False
    
    if not analysis_results:
        print("❌ 没有成功分析的期权")
        return False
    
    # 6. 转换为DataFrame并筛选
    print("📋 筛选期权...")
    results_df = pd.DataFrame(analysis_results)
    
    # 应用筛选条件
    filtered_df = results_df[
        (results_df['annualized_return'] >= 0.15) &  # 年化收益率 > 15%
        (results_df['assignment_probability'] <= 0.4) &  # 被指派概率 < 40%
        (results_df['volume'] >= 50) &  # 成交量 > 50
        (results_df['dte'] <= 45) &  # 到期天数 <= 45
        (results_df['strike_price'] < stock_info['current_price'])  # 价外期权
    ].copy()
    
    print(f"   筛选前期权数量: {len(results_df)}")
    print(f"   筛选后期权数量: {len(filtered_df)}")
    
    if filtered_df.empty:
        print("⚠️ 没有符合筛选条件的期权")
    else:
        print("✅ 找到符合筛选条件的期权")
        best_option = filtered_df.iloc[0]
        print(f"   最佳期权: 行权价 ${best_option['strike_price']:.1f}")
        print(f"   年化收益率: {best_option['annualized_return']:.1%}")
        print(f"   被指派概率: {best_option['assignment_probability']:.1%}")
    
    print("✅ 单股票期权分析功能测试通过！")
    return True

if __name__ == "__main__":
    success = test_single_stock_analysis()
    if success:
        print("\n🎉 所有测试通过！单股票分析功能正常工作。")
    else:
        print("\n❌ 测试失败！请检查错误信息。")
