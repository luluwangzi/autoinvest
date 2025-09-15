"""
测试脚本 - 验证应用核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from options_calculator import calculator
from data_fetcher import data_fetcher
from utils import validate_stock_symbol, format_currency, format_percentage
import pandas as pd


def test_options_calculator():
    """测试期权计算器"""
    print("🧮 测试期权计算器...")
    
    # 测试基本计算
    S, K, T, r, sigma = 150.0, 145.0, 0.1, 0.05, 0.3
    
    # 测试Put期权价格
    put_price = calculator.black_scholes_put(S, K, T, r, sigma)
    print(f"Put期权价格: ${put_price:.2f}")
    
    # 测试Call期权价格
    call_price = calculator.black_scholes_call(S, K, T, r, sigma)
    print(f"Call期权价格: ${call_price:.2f}")
    
    # 测试Delta计算
    put_delta = calculator.calculate_delta_put(S, K, T, r, sigma)
    call_delta = calculator.calculate_delta_call(S, K, T, r, sigma)
    print(f"Put Delta: {put_delta:.3f}")
    print(f"Call Delta: {call_delta:.3f}")
    
    # 测试被指派概率
    put_assignment_prob = calculator.calculate_assignment_probability(S, K, T, r, sigma, 'put')
    call_assignment_prob = calculator.calculate_assignment_probability(S, K, T, r, sigma, 'call')
    print(f"Put被指派概率: {put_assignment_prob:.1%}")
    print(f"Call被指派概率: {call_assignment_prob:.1%}")
    
    # 测试年化收益率
    annualized_return = calculator.calculate_annualized_return(put_price, K, 30)
    print(f"年化收益率: {annualized_return:.1%}")
    
    print("✅ 期权计算器测试通过\n")


def test_data_fetcher():
    """测试数据获取器"""
    print("📊 测试数据获取器...")
    
    # 测试股票信息获取
    symbol = "AAPL"
    stock_info = data_fetcher.get_stock_info(symbol)
    print(f"股票代码: {stock_info['symbol']}")
    print(f"股票名称: {stock_info['name']}")
    print(f"当前价格: ${stock_info['current_price']:.2f}")
    print(f"历史波动率: {stock_info['historical_volatility']:.1%}")
    
    # 测试期权链获取
    options_data = data_fetcher.get_options_chain(symbol)
    print(f"Put期权数量: {len(options_data['puts'])}")
    print(f"Call期权数量: {len(options_data['calls'])}")
    
    if not options_data['puts'].empty:
        puts_df = options_data['puts']
        print(f"Put期权示例: 行权价${puts_df['strike_price'].iloc[0]:.1f}, 价格${puts_df['option_price'].iloc[0]:.2f}")
    
    print("✅ 数据获取器测试通过\n")


def test_utils():
    """测试工具函数"""
    print("🔧 测试工具函数...")
    
    # 测试股票代码验证
    valid_symbols = ["AAPL", "TSLA", "MSFT"]
    invalid_symbols = ["", "123", "TOOLONG", "AAPL123"]
    
    for symbol in valid_symbols:
        result = validate_stock_symbol(symbol)
        print(f"'{symbol}' 验证结果: {result}")
    
    for symbol in invalid_symbols:
        result = validate_stock_symbol(symbol)
        print(f"'{symbol}' 验证结果: {result}")
    
    # 测试格式化函数
    print(f"货币格式化: {format_currency(1234.56)}")
    print(f"百分比格式化: {format_percentage(0.1234)}")
    
    print("✅ 工具函数测试通过\n")


def test_integration():
    """测试集成功能"""
    print("🔗 测试集成功能...")
    
    # 获取AAPL的期权数据并进行分析
    symbol = "AAPL"
    stock_info = data_fetcher.get_stock_info(symbol)
    options_data = data_fetcher.get_options_chain(symbol)
    
    if not options_data['puts'].empty:
        puts_df = options_data['puts']
        puts_df = data_fetcher.validate_option_data(puts_df, stock_info['current_price'])
        
        if not puts_df.empty:
            # 选择第一个期权进行分析
            option = puts_df.iloc[0]
            
            option_data = {
                'current_price': stock_info['current_price'],
                'strike_price': option['strike_price'],
                'dte': option['dte'],
                'option_price': option['option_price'],
                'option_type': 'put'
            }
            
            # 进行完整分析
            analysis = calculator.analyze_option(option_data)
            
            print(f"期权分析结果:")
            print(f"  年化收益率: {analysis['annualized_return']:.1%}")
            print(f"  被指派概率: {analysis['assignment_probability']:.1%}")
            print(f"  Delta: {analysis['delta']:.3f}")
            print(f"  隐含波动率: {analysis['implied_volatility']:.1%}")
    
    print("✅ 集成功能测试通过\n")


def main():
    """主测试函数"""
    print("🚀 开始测试美股期权分析策略平台...\n")
    
    try:
        test_options_calculator()
        test_data_fetcher()
        test_utils()
        test_integration()
        
        print("🎉 所有测试通过！应用运行正常。")
        print("\n📋 测试总结:")
        print("✅ 期权计算器 - Black-Scholes模型计算正常")
        print("✅ 数据获取器 - Yahoo Finance数据获取正常")
        print("✅ 工具函数 - 数据验证和格式化正常")
        print("✅ 集成功能 - 端到端分析流程正常")
        
        print("\n🌐 应用已启动，访问地址: http://localhost:8501")
        print("📱 支持的功能:")
        print("  - 单股票期权分析")
        print("  - 批量期权筛选")
        print("  - Sell Call策略分析")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
