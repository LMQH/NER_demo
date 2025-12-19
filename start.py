"""
Windows启动脚本
"""
import sys
import os
from pathlib import Path

# 获取项目根目录
project_root = Path(__file__).parent

# 切换到项目根目录
os.chdir(project_root)

# 添加项目根目录到Python路径
sys.path.insert(0, str(project_root))

# 运行主程序
if __name__ == "__main__":
    from src.main import main
    sys.exit(main())

