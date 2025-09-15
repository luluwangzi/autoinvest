"""
工具函数模块
包含数据验证、错误处理、日志记录等实用功能
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')


def setup_logging():
    """设置日志记录"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def validate_stock_symbol(symbol: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        symbol: 股票代码
        
    Returns:
        是否为有效格式
    """
    if not symbol or not isinstance(symbol, str):
        return False
    
    # 基本格式检查
    symbol = symbol.upper().strip()
    
    # 长度检查
    if len(symbol) < 1 or len(symbol) > 5:
        return False
    
    # 字符检查（只允许字母）
    if not symbol.isalpha():
        return False
    
    return True


def validate_option_data(option_data: pd.DataFrame) -> pd.DataFrame:
    """
    验证和清理期权数据
    
    Args:
        option_data: 期权数据DataFrame
        
    Returns:
        清理后的期权数据DataFrame
    """
    if option_data.empty:
        return option_data
    
    original_count = len(option_data)
    
    # 移除完全空的行
    option_data = option_data.dropna(how='all')
    
    # 移除关键字段为空的行
    required_fields = ['strike_price', 'option_price']
    for field in required_fields:
        if field in option_data.columns:
            option_data = option_data.dropna(subset=[field])
    
    # 数据类型转换和验证
    numeric_fields = ['strike_price', 'option_price', 'bid_price', 'ask_price', 
                     'volume', 'open_interest', 'implied_volatility']
    
    for field in numeric_fields:
        if field in option_data.columns:
            # 转换为数值类型
            option_data[field] = pd.to_numeric(option_data[field], errors='coerce')
            # 移除无效值
            option_data = option_data.dropna(subset=[field])
    
    # 移除异常值
    if 'strike_price' in option_data.columns:
        option_data = option_data[option_data['strike_price'] > 0]
    
    if 'option_price' in option_data.columns:
        option_data = option_data[option_data['option_price'] > 0]
    
    if 'volume' in option_data.columns:
        option_data = option_data[option_data['volume'] >= 0]
    
    if 'implied_volatility' in option_data.columns:
        # 移除异常高的IV值
        option_data = option_data[option_data['implied_volatility'] <= 5.0]
        option_data = option_data[option_data['implied_volatility'] >= 0.01]
    
    # 填充缺失的IV值
    if 'implied_volatility' in option_data.columns:
        option_data['implied_volatility'] = option_data['implied_volatility'].fillna(0.3)
    
    cleaned_count = len(option_data)
    
    if original_count != cleaned_count:
        print(f"数据清理: {original_count} -> {cleaned_count} 条记录")
    
    return option_data


def validate_calculation_inputs(S: float, K: float, T: float, r: float, sigma: float) -> bool:
    """
    验证期权计算输入参数
    
    Args:
        S: 当前股价
        K: 行权价
        T: 到期时间
        r: 无风险利率
        sigma: 波动率
        
    Returns:
        参数是否有效
    """
    # 检查基本类型
    if not all(isinstance(x, (int, float)) for x in [S, K, T, r, sigma]):
        return False
    
    # 检查数值范围
    if S <= 0 or K <= 0:
        return False
    
    if T < 0:
        return False
    
    if r < 0 or r > 1:  # 利率应该在0-100%之间
        return False
    
    if sigma < 0 or sigma > 5:  # 波动率应该在0-500%之间
        return False
    
    return True


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    安全除法，避免除零错误
    
    Args:
        numerator: 分子
        denominator: 分母
        default: 默认值
        
    Returns:
        除法结果或默认值
    """
    try:
        if denominator == 0 or np.isnan(denominator) or np.isinf(denominator):
            return default
        if np.isnan(numerator) or np.isinf(numerator):
            return default
        return numerator / denominator
    except:
        return default


def format_currency(value: float, decimals: int = 2) -> str:
    """
    格式化货币显示
    
    Args:
        value: 数值
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    try:
        if np.isnan(value) or np.isinf(value):
            return "N/A"
        return f"${value:,.{decimals}f}"
    except:
        return "N/A"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    格式化百分比显示
    
    Args:
        value: 数值（小数形式）
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    try:
        if np.isnan(value) or np.isinf(value):
            return "N/A"
        return f"{value:.{decimals}%}"
    except:
        return "N/A"


def format_number(value: float, decimals: int = 2) -> str:
    """
    格式化数字显示
    
    Args:
        value: 数值
        decimals: 小数位数
        
    Returns:
        格式化后的字符串
    """
    try:
        if np.isnan(value) or np.isinf(value):
            return "N/A"
        return f"{value:,.{decimals}f}"
    except:
        return "N/A"


def calculate_risk_score(assignment_prob: float, annual_return: float) -> str:
    """
    计算风险评分
    
    Args:
        assignment_prob: 被指派概率
        annual_return: 年化收益率
        
    Returns:
        风险等级
    """
    try:
        # 基于被指派概率和收益率的综合评分
        risk_score = assignment_prob * 0.7 + (1 - min(annual_return, 2.0) / 2.0) * 0.3
        
        if risk_score < 0.3:
            return "🟢 低风险"
        elif risk_score < 0.6:
            return "🟡 中等风险"
        else:
            return "🔴 高风险"
    except:
        return "❓ 未知风险"


def get_market_hours() -> Dict[str, Any]:
    """
    获取市场交易时间信息
    
    Returns:
        包含市场时间信息的字典
    """
    now = datetime.now()
    
    # 美股交易时间（东部时间）
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # 检查是否为工作日
    is_weekday = now.weekday() < 5
    
    # 检查是否在交易时间内
    is_market_hours = is_weekday and market_open <= now <= market_close
    
    return {
        'is_market_open': is_market_hours,
        'is_weekday': is_weekday,
        'market_open': market_open,
        'market_close': market_close,
        'current_time': now
    }


def handle_api_error(error: Exception, context: str = "") -> str:
    """
    处理API错误
    
    Args:
        error: 异常对象
        context: 错误上下文
        
    Returns:
        用户友好的错误消息
    """
    error_msg = str(error).lower()
    
    if "timeout" in error_msg or "connection" in error_msg:
        return f"网络连接超时，请检查网络连接后重试。{context}"
    elif "not found" in error_msg or "404" in error_msg:
        return f"未找到相关数据，请检查股票代码是否正确。{context}"
    elif "rate limit" in error_msg or "too many requests" in error_msg:
        return f"请求过于频繁，请稍后重试。{context}"
    elif "permission" in error_msg or "unauthorized" in error_msg:
        return f"访问权限不足，请稍后重试。{context}"
    else:
        return f"数据获取失败，请稍后重试。{context}"


def create_summary_stats(data: pd.DataFrame) -> Dict[str, Any]:
    """
    创建数据摘要统计
    
    Args:
        data: 数据DataFrame
        
    Returns:
        包含统计信息的字典
    """
    if data.empty:
        return {}
    
    stats = {}
    
    # 基本统计
    stats['count'] = len(data)
    stats['unique_symbols'] = data['symbol'].nunique() if 'symbol' in data.columns else 0
    
    # 数值字段统计
    numeric_fields = ['annualized_return', 'assignment_probability', 'volume', 'dte']
    
    for field in numeric_fields:
        if field in data.columns:
            stats[f'{field}_mean'] = data[field].mean()
            stats[f'{field}_median'] = data[field].median()
            stats[f'{field}_std'] = data[field].std()
            stats[f'{field}_min'] = data[field].min()
            stats[f'{field}_max'] = data[field].max()
    
    return stats


def filter_options_by_criteria(data: pd.DataFrame, criteria: Dict[str, Any]) -> pd.DataFrame:
    """
    根据条件筛选期权数据
    
    Args:
        data: 期权数据DataFrame
        criteria: 筛选条件字典
        
    Returns:
        筛选后的数据DataFrame
    """
    if data.empty:
        return data
    
    filtered_data = data.copy()
    
    # 应用筛选条件
    if 'min_annual_return' in criteria:
        filtered_data = filtered_data[filtered_data['annualized_return'] >= criteria['min_annual_return']]
    
    if 'max_assignment_prob' in criteria:
        filtered_data = filtered_data[filtered_data['assignment_probability'] <= criteria['max_assignment_prob']]
    
    if 'min_volume' in criteria:
        filtered_data = filtered_data[filtered_data['volume'] >= criteria['min_volume']]
    
    if 'max_dte' in criteria:
        filtered_data = filtered_data[filtered_data['dte'] <= criteria['max_dte']]
    
    if 'min_dte' in criteria:
        filtered_data = filtered_data[filtered_data['dte'] >= criteria['min_dte']]
    
    if 'min_strike_price' in criteria:
        filtered_data = filtered_data[filtered_data['strike_price'] >= criteria['min_strike_price']]
    
    if 'max_strike_price' in criteria:
        filtered_data = filtered_data[filtered_data['strike_price'] <= criteria['max_strike_price']]
    
    return filtered_data


def create_performance_metrics(data: pd.DataFrame) -> Dict[str, Any]:
    """
    创建性能指标
    
    Args:
        data: 期权数据DataFrame
        
    Returns:
        包含性能指标的字典
    """
    if data.empty:
        return {}
    
    metrics = {}
    
    # 收益指标
    if 'annualized_return' in data.columns:
        metrics['avg_annual_return'] = data['annualized_return'].mean()
        metrics['median_annual_return'] = data['annualized_return'].median()
        metrics['max_annual_return'] = data['annualized_return'].max()
        metrics['min_annual_return'] = data['annualized_return'].min()
    
    # 风险指标
    if 'assignment_probability' in data.columns:
        metrics['avg_assignment_prob'] = data['assignment_probability'].mean()
        metrics['median_assignment_prob'] = data['assignment_probability'].median()
        metrics['max_assignment_prob'] = data['assignment_probability'].max()
        metrics['min_assignment_prob'] = data['assignment_probability'].min()
    
    # 流动性指标
    if 'volume' in data.columns:
        metrics['total_volume'] = data['volume'].sum()
        metrics['avg_volume'] = data['volume'].mean()
        metrics['median_volume'] = data['volume'].median()
    
    # 时间指标
    if 'dte' in data.columns:
        metrics['avg_dte'] = data['dte'].mean()
        metrics['median_dte'] = data['dte'].median()
        metrics['min_dte'] = data['dte'].min()
        metrics['max_dte'] = data['dte'].max()
    
    return metrics


# 创建全局日志记录器
logger = setup_logging()
