"""
Streamlit Cloud 部署入口文件
这个文件是Streamlit Cloud的默认入口点
"""

import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入主应用
from app import main

if __name__ == "__main__":
    main()
