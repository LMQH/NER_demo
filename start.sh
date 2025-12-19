#!/bin/bash

# Linux启动脚本

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 设置Python路径
export PYTHONPATH="$SCRIPT_DIR/src:$PYTHONPATH"

# 运行主程序
python3 -m src.main

# 返回退出码
exit $?

