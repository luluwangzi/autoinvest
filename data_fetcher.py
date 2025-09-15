"""
数据获取模块 - Yahoo Finance集成
实现股票数据、期权链数据和市场数据的获取
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import requests
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from utils import validate_stock_symbol, handle_api_error, logger


class DataFetcher:
    """数据获取器类，负责从Yahoo Finance获取各种市场数据"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息
        
        Args:
            symbol: 股票代码
            
        Returns:
            包含股票信息的字典
        """
        # 验证股票代码
        if not validate_stock_symbol(symbol):
            logger.warning(f"Invalid stock symbol: {symbol}")
            return self._get_default_stock_info(symbol)
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 获取当前价格
            hist = ticker.history(period="1d")
            current_price = hist['Close'].iloc[-1] if not hist.empty else info.get('currentPrice', 0)
            
            # 获取历史波动率
            hist_30d = ticker.history(period="30d")
            if len(hist_30d) > 1:
                returns = hist_30d['Close'].pct_change().dropna()
                historical_volatility = returns.std() * np.sqrt(252)  # 年化波动率
            else:
                historical_volatility = 0.3  # 默认30%
            
            logger.info(f"Successfully fetched stock info for {symbol}")
            return {
                'symbol': symbol,
                'current_price': current_price,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap', 0),
                'historical_volatility': historical_volatility,
                'dividend_yield': info.get('dividendYield', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'beta': info.get('beta', 1.0),
                'last_updated': datetime.now()
            }
        except Exception as e:
            error_msg = handle_api_error(e, f"获取 {symbol} 股票信息时")
            logger.error(f"Error fetching stock info for {symbol}: {e}")
            return self._get_default_stock_info(symbol)
    
    def _get_default_stock_info(self, symbol: str) -> Dict:
        """获取默认股票信息"""
        return {
            'symbol': symbol,
            'current_price': 0,
            'name': symbol,
            'sector': 'Unknown',
            'industry': 'Unknown',
            'market_cap': 0,
            'historical_volatility': 0.3,
            'dividend_yield': 0,
            'pe_ratio': 0,
            'beta': 1.0,
            'last_updated': datetime.now()
        }
    
    def get_options_chain(self, symbol: str, expiration_date: str = None) -> Dict:
        """
        获取期权链数据
        
        Args:
            symbol: 股票代码
            expiration_date: 到期日期 (YYYY-MM-DD格式)，如果为None则获取最近的到期日
            
        Returns:
            包含期权链数据的字典
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # 获取可用的到期日期
            expirations = ticker.options
            if not expirations:
                return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
            
            # 选择到期日期
            if expiration_date is None:
                # 选择最近的到期日
                exp_date = expirations[0]
            else:
                # 找到最接近指定日期的到期日
                target_date = pd.to_datetime(expiration_date)
                exp_date = min(expirations, key=lambda x: abs(pd.to_datetime(x) - target_date))
            
            # 获取期权链
            options_chain = ticker.option_chain(exp_date)
            
            # 计算到期天数
            exp_datetime = pd.to_datetime(exp_date)
            dte = (exp_datetime - datetime.now()).days
            
            # 处理Calls数据
            calls_df = options_chain.calls.copy()
            if not calls_df.empty:
                calls_df['option_type'] = 'call'
                calls_df['expiration_date'] = exp_date
                calls_df['dte'] = dte
                calls_df['symbol'] = symbol
                # 重命名列以保持一致性
                calls_df = calls_df.rename(columns={
                    'strike': 'strike_price',
                    'lastPrice': 'option_price',
                    'bid': 'bid_price',
                    'ask': 'ask_price',
                    'volume': 'volume',
                    'openInterest': 'open_interest',
                    'impliedVolatility': 'implied_volatility'
                })
            
            # 处理Puts数据
            puts_df = options_chain.puts.copy()
            if not puts_df.empty:
                puts_df['option_type'] = 'put'
                puts_df['expiration_date'] = exp_date
                puts_df['dte'] = dte
                puts_df['symbol'] = symbol
                # 重命名列以保持一致性
                puts_df = puts_df.rename(columns={
                    'strike': 'strike_price',
                    'lastPrice': 'option_price',
                    'bid': 'bid_price',
                    'ask': 'ask_price',
                    'volume': 'volume',
                    'openInterest': 'open_interest',
                    'impliedVolatility': 'implied_volatility'
                })
            
            return {
                'calls': calls_df,
                'puts': puts_df,
                'expiration_date': exp_date,
                'dte': dte
            }
        except Exception as e:
            print(f"Error fetching options chain for {symbol}: {e}")
            return {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
    
    def get_multiple_options_chains(self, symbols: List[str], max_dte: int = 45) -> Dict[str, Dict]:
        """
        批量获取多个股票的期权链数据
        
        Args:
            symbols: 股票代码列表
            max_dte: 最大到期天数
            
        Returns:
            包含所有股票期权链数据的字典
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            try:
                print(f"Fetching options for {symbol} ({i+1}/{len(symbols)})")
                
                # 获取股票信息
                stock_info = self.get_stock_info(symbol)
                
                # 获取期权链
                options_data = self.get_options_chain(symbol)
                
                # 过滤到期天数
                if not options_data['puts'].empty:
                    options_data['puts'] = options_data['puts'][options_data['puts']['dte'] <= max_dte]
                if not options_data['calls'].empty:
                    options_data['calls'] = options_data['calls'][options_data['calls']['dte'] <= max_dte]
                
                results[symbol] = {
                    'stock_info': stock_info,
                    'options': options_data
                }
                
                # 添加延迟避免请求过于频繁
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                results[symbol] = {
                    'stock_info': {'symbol': symbol, 'current_price': 0, 'name': symbol},
                    'options': {'calls': pd.DataFrame(), 'puts': pd.DataFrame()}
                }
        
        return results
    
    def get_nasdaq100_symbols(self) -> List[str]:
        """
        获取纳斯达克100成分股列表
        
        Returns:
            股票代码列表
        """
        try:
            # 从Wikipedia获取纳斯达克100成分股
            url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            response = self.session.get(url)
            
            if response.status_code == 200:
                # 使用pandas读取HTML表格
                tables = pd.read_html(response.text)
                
                # 找到包含股票代码的表格
                for table in tables:
                    if 'Ticker' in table.columns or 'Symbol' in table.columns:
                        # 获取股票代码列
                        symbol_col = 'Ticker' if 'Ticker' in table.columns else 'Symbol'
                        symbols = table[symbol_col].tolist()
                        
                        # 清理数据，只保留有效的股票代码
                        valid_symbols = []
                        for symbol in symbols:
                            if isinstance(symbol, str) and len(symbol) <= 5 and symbol.isalpha():
                                valid_symbols.append(symbol.upper())
                        
                        return valid_symbols[:100]  # 限制为100只股票
            
            # 如果网络获取失败，返回一些主要股票代码
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
                'PYPL', 'INTC', 'CMCSA', 'PEP', 'COST', 'TMUS', 'AVGO', 'TXN', 'QCOM', 'CHTR',
                'AMGN', 'HON', 'INTU', 'BKNG', 'GILD', 'ISRG', 'VRTX', 'MDLZ', 'FISV', 'REGN',
                'ADP', 'CSX', 'ATVI', 'ILMN', 'LRCX', 'ADI', 'CTAS', 'KLAC', 'SNPS', 'MRNA',
                'ORLY', 'IDXX', 'DXCM', 'EXC', 'XEL', 'WBA', 'CTSH', 'FAST', 'PAYX', 'ROST',
                'PCAR', 'BIIB', 'ALGN', 'SIRI', 'VRSK', 'INCY', 'WLTW', 'MXIM', 'CDNS', 'CHKP',
                'MELI', 'CTXS', 'NTES', 'SWKS', 'VRSN', 'FANG', 'LULU', 'NTAP', 'CERN', 'SGEN',
                'SIVB', 'WDAY', 'ULTA', 'CPRT', 'SPLK', 'DOCU', 'OKTA', 'ZM', 'CRWD', 'DDOG',
                'NET', 'SNOW', 'PLTR', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'UPST', 'AFRM', 'OPEN'
            ]
            
        except Exception as e:
            print(f"Error fetching NASDAQ 100 symbols: {e}")
            # 返回一些主要股票代码作为备选
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'ADBE', 'CRM',
                'PYPL', 'INTC', 'CMCSA', 'PEP', 'COST', 'TMUS', 'AVGO', 'TXN', 'QCOM', 'CHTR'
            ]
    
    def get_market_status(self) -> Dict:
        """
        获取市场状态信息
        
        Returns:
            包含市场状态的字典
        """
        try:
            # 获取SPY数据来判断市场状态
            spy = yf.Ticker("SPY")
            hist = spy.history(period="1d")
            
            if hist.empty:
                return {'is_market_open': False, 'market_status': 'Unknown'}
            
            # 检查是否有实时数据
            last_update = hist.index[-1]
            now = datetime.now()
            
            # 简单判断：如果最后更新时间是今天且接近当前时间，认为市场开放
            if (last_update.date() == now.date() and 
                abs((now - last_update).total_seconds()) < 3600):  # 1小时内
                return {'is_market_open': True, 'market_status': 'Open'}
            else:
                return {'is_market_open': False, 'market_status': 'Closed'}
                
        except Exception as e:
            print(f"Error checking market status: {e}")
            return {'is_market_open': False, 'market_status': 'Unknown'}
    
    def validate_option_data(self, option_data: pd.DataFrame, current_price: float) -> pd.DataFrame:
        """
        验证和清理期权数据
        
        Args:
            option_data: 期权数据DataFrame
            current_price: 当前股价
            
        Returns:
            清理后的期权数据DataFrame
        """
        if option_data.empty:
            return option_data
        
        # 移除无效数据
        option_data = option_data.dropna(subset=['strike_price', 'option_price'])
        
        # 移除价格为0的期权
        option_data = option_data[option_data['option_price'] > 0]
        
        # 移除成交量过低的期权
        option_data = option_data[option_data['volume'] >= 1]
        
        # 修复隐含波动率异常值
        if 'implied_volatility' in option_data.columns:
            # 移除异常高的IV值
            option_data = option_data[option_data['implied_volatility'] <= 5.0]
            # 填充缺失的IV值
            option_data['implied_volatility'] = option_data['implied_volatility'].fillna(0.3)
        
        # 确保数据类型正确
        numeric_columns = ['strike_price', 'option_price', 'bid_price', 'ask_price', 
                          'volume', 'open_interest', 'implied_volatility']
        for col in numeric_columns:
            if col in option_data.columns:
                option_data[col] = pd.to_numeric(option_data[col], errors='coerce')
        
        return option_data.dropna(subset=['strike_price', 'option_price'])


# 创建全局数据获取器实例
data_fetcher = DataFetcher()
