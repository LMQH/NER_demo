#!/bin/bash

# Linux启动脚本
# 启动FastAPI API服务

# 获取脚本所在目录（项目根目录）
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目根目录
cd "$SCRIPT_DIR"

# 设置Python路径
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "============================================================"
echo "NER Demo API服务启动 (FastAPI)"
echo "============================================================"
echo "正在启动服务..."
echo "API文档: http://localhost:8000/docs"
echo "API文档 (ReDoc): http://localhost:8000/redoc"
echo "============================================================"
echo "按 Ctrl+C 停止服务"
echo "============================================================"

# 启动FastAPI服务
# 使用 reload=True 支持热重载（开发模式）
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

