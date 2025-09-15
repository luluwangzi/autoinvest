"""
期权计算模块 - 基于Black-Scholes模型
实现期权定价、Greeks计算和风险指标分析
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import minimize_scalar
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class OptionsCalculator:
    """期权计算器类，基于Black-Scholes模型"""
    
    def __init__(self):
        self.risk_free_rate = 0.05  # 默认无风险利率5%
    
    def set_risk_free_rate(self, rate: float):
        """设置无风险利率"""
        self.risk_free_rate = rate
    
    def black_scholes_put(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        计算Put期权价格
        
        Args:
            S: 当前股价
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            sigma: 波动率
            
        Returns:
            Put期权价格
        """
        if T <= 0:
            return max(K - S, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
        return max(put_price, 0)
    
    def black_scholes_call(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """
        计算Call期权价格
        
        Args:
            S: 当前股价
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            sigma: 波动率
            
        Returns:
            Call期权价格
        """
        if T <= 0:
            return max(S - K, 0)
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
        return max(call_price, 0)
    
    def calculate_d1_d2(self, S: float, K: float, T: float, r: float, sigma: float) -> Tuple[float, float]:
        """计算d1和d2参数"""
        if T <= 0:
            return 0, 0
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        return d1, d2
    
    def calculate_delta_put(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Put期权的Delta"""
        if T <= 0:
            return -1 if S < K else 0
        
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        return -norm.cdf(-d1)
    
    def calculate_delta_call(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Call期权的Delta"""
        if T <= 0:
            return 1 if S > K else 0
        
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        return norm.cdf(d1)
    
    def calculate_gamma(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Gamma"""
        if T <= 0:
            return 0
        
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        return norm.pdf(d1) / (S * sigma * np.sqrt(T))
    
    def calculate_theta_put(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Put期权的Theta"""
        if T <= 0:
            return 0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                - r * K * np.exp(-r * T) * norm.cdf(-d2))
        return theta / 365  # 转换为每日theta
    
    def calculate_theta_call(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Call期权的Theta"""
        if T <= 0:
            return 0
        
        d1, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        theta = (-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T)) 
                + r * K * np.exp(-r * T) * norm.cdf(d2))
        return theta / 365  # 转换为每日theta
    
    def calculate_vega(self, S: float, K: float, T: float, r: float, sigma: float) -> float:
        """计算Vega"""
        if T <= 0:
            return 0
        
        d1, _ = self.calculate_d1_d2(S, K, T, r, sigma)
        return S * norm.pdf(d1) * np.sqrt(T) / 100  # 转换为1%波动率变化
    
    def calculate_assignment_probability(self, S: float, K: float, T: float, r: float, sigma: float, option_type: str = 'put') -> float:
        """
        计算被指派概率
        
        Args:
            S: 当前股价
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            sigma: 波动率
            option_type: 期权类型 ('put' 或 'call')
            
        Returns:
            被指派概率 (0-1)
        """
        if T <= 0:
            if option_type == 'put':
                return 1.0 if S <= K else 0.0
            else:
                return 1.0 if S >= K else 0.0
        
        _, d2 = self.calculate_d1_d2(S, K, T, r, sigma)
        
        if option_type == 'put':
            return norm.cdf(-d2)  # Put期权被指派概率
        else:
            return norm.cdf(d2)   # Call期权被指派概率
    
    def calculate_annualized_return(self, option_price: float, strike_price: float, dte: int) -> float:
        """
        计算年化收益率
        
        Args:
            option_price: 期权价格
            strike_price: 行权价
            dte: 到期天数
            
        Returns:
            年化收益率 (小数形式)
        """
        if dte <= 0 or option_price <= 0:
            return 0.0
        
        return (option_price / strike_price) * (365 / dte)
    
    def calculate_breakeven_price(self, strike_price: float, option_price: float, option_type: str = 'put') -> float:
        """
        计算盈亏平衡价格
        
        Args:
            strike_price: 行权价
            option_price: 期权价格
            option_type: 期权类型 ('put' 或 'call')
            
        Returns:
            盈亏平衡价格
        """
        if option_type == 'put':
            return strike_price - option_price
        else:
            return strike_price + option_price
    
    def calculate_max_profit_loss(self, option_price: float, strike_price: float, current_price: float, option_type: str = 'put') -> Dict[str, float]:
        """
        计算最大盈利和最大亏损
        
        Args:
            option_price: 期权价格
            strike_price: 行权价
            current_price: 当前股价
            option_type: 期权类型 ('put' 或 'call')
            
        Returns:
            包含最大盈利和最大亏损的字典
        """
        if option_type == 'put':
            max_profit = option_price
            max_loss = strike_price - option_price
        else:
            max_profit = option_price
            max_loss = float('inf')  # Call期权理论上无限亏损
        
        return {
            'max_profit': max_profit,
            'max_loss': max_loss
        }
    
    def calculate_implied_volatility(self, market_price: float, S: float, K: float, T: float, r: float, option_type: str = 'put') -> float:
        """
        计算隐含波动率
        
        Args:
            market_price: 市场价格
            S: 当前股价
            K: 行权价
            T: 到期时间（年）
            r: 无风险利率
            option_type: 期权类型 ('put' 或 'call')
            
        Returns:
            隐含波动率
        """
        def objective(sigma):
            if option_type == 'put':
                theoretical_price = self.black_scholes_put(S, K, T, r, sigma)
            else:
                theoretical_price = self.black_scholes_call(S, K, T, r, sigma)
            return (theoretical_price - market_price) ** 2
        
        try:
            result = minimize_scalar(objective, bounds=(0.01, 5.0), method='bounded')
            return result.x if result.success else 0.3  # 默认30%波动率
        except:
            return 0.3  # 默认30%波动率
    
    def analyze_option(self, option_data: Dict) -> Dict:
        """
        综合分析单个期权
        
        Args:
            option_data: 期权数据字典，包含股价、行权价、到期时间、期权价格等
            
        Returns:
            包含所有分析指标的字典
        """
        S = option_data['current_price']
        K = option_data['strike_price']
        T = option_data['dte'] / 365.0
        r = self.risk_free_rate
        option_price = option_data['option_price']
        option_type = option_data.get('option_type', 'put')
        
        # 计算隐含波动率
        iv = self.calculate_implied_volatility(option_price, S, K, T, r, option_type)
        
        # 计算Greeks
        if option_type == 'put':
            delta = self.calculate_delta_put(S, K, T, r, iv)
            theta = self.calculate_theta_put(S, K, T, r, iv)
        else:
            delta = self.calculate_delta_call(S, K, T, r, iv)
            theta = self.calculate_theta_call(S, K, T, r, iv)
        
        gamma = self.calculate_gamma(S, K, T, r, iv)
        vega = self.calculate_vega(S, K, T, r, iv)
        
        # 计算风险指标
        assignment_prob = self.calculate_assignment_probability(S, K, T, r, iv, option_type)
        annualized_return = self.calculate_annualized_return(option_price, K, option_data['dte'])
        breakeven_price = self.calculate_breakeven_price(K, option_price, option_type)
        max_profit_loss = self.calculate_max_profit_loss(option_price, K, S, option_type)
        
        return {
            'implied_volatility': iv,
            'delta': delta,
            'gamma': gamma,
            'theta': theta,
            'vega': vega,
            'assignment_probability': assignment_prob,
            'annualized_return': annualized_return,
            'breakeven_price': breakeven_price,
            'max_profit': max_profit_loss['max_profit'],
            'max_loss': max_profit_loss['max_loss'],
            'risk_reward_ratio': max_profit_loss['max_profit'] / max_profit_loss['max_loss'] if max_profit_loss['max_loss'] > 0 else float('inf')
        }


# 创建全局计算器实例
calculator = OptionsCalculator()
