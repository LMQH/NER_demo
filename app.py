"""
NER Demo FastAPI服务
提供RESTful API接口，支持前端传入文本和模型选择进行实体抽取
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

# 加载环境变量文件（优先加载 .env，如果不存在则尝试 dev.env）
env_file = project_root / '.env'
if not env_file.exists():
    env_file = project_root / 'dev.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file.name}")
else:
    print("⚠ 未找到 .env 或 dev.env 文件，将使用系统环境变量")

from src.model_manager import ModelManager
from src.processors import FileReader
from src.config import ConfigManager
from src.database import DatabaseConnection
from src.api.dependencies import init_dependencies
from src.api.routes import system, extract, file

# 配置日志系统
log_dir = project_root / "logs"
log_dir.mkdir(exist_ok=True)

# 创建日志文件名（按日期）
log_file = log_dir / f"inference_{datetime.now().strftime('%Y%m%d')}.log"

# 配置日志格式和处理器
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()  # 同时输出到控制台
    ]
)

logger = logging.getLogger("NER_API")

# 创建FastAPI应用
app = FastAPI(
    title="NER Demo API",
    description="基于ModelScope的中文命名实体识别（NER）API服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化模型管理器和文件读取器
model_manager = ModelManager(base_path=str(project_root))
file_reader = FileReader()
config_manager = ConfigManager()

# 测试MySQL数据库连接
db_connection = None
db_status = "未配置"
try:
    db_connection = DatabaseConnection()
    if db_connection.test_connection():
        db_status = "✓ 连接成功"
        logger.info(f"MySQL数据库连接成功 - Host: {db_connection.host}, Database: {db_connection.database}")
    else:
        db_status = "✗ 连接失败"
        logger.warning("MySQL数据库连接测试失败")
except Exception as e:
    db_status = f"✗ 连接失败: {str(e)}"
    logger.error(f"MySQL数据库连接初始化失败: {str(e)}")

# 初始化依赖项（传入已测试的数据库连接）
init_dependencies(model_manager, file_reader, config_manager, project_root, db_connection)

# 注册路由
app.include_router(system.router)
app.include_router(extract.router)
app.include_router(file.router)

if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("NER Demo API服务启动 (FastAPI)")
    print("=" * 60)
    
    # 显示MySQL数据库连接状态
    print(f"MySQL数据库: {db_status}")
    if db_connection:
        print(f"  主机: {db_connection.host}:{db_connection.port}")
        print(f"  数据库: {db_connection.database}")
        print(f"  用户: {db_connection.user}")
    
    print(f"支持的模型: {', '.join(model_manager.list_models())}")
    api_key = os.getenv('DASHSCOPE_API_KEY')
    qwen_status = '已启用' if (api_key and api_key.strip() and api_key != 'your_api_key_here') else '未配置（需要DASHSCOPE_API_KEY）'
    print(f"Qwen-Flash模型: {qwen_status}")
    print(f"API文档: http://localhost:8000/docs")
    print(f"API文档 (ReDoc): http://localhost:8000/redoc")
    print("=" * 60)
    
    # 启动FastAPI服务
    # 默认运行在 http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
