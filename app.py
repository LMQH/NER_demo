"""
NER Demo FastAPI服务
提供RESTful API接口，支持前端传入文本和模型选择进行实体抽取
"""
import sys
import os
import shutil
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)

from src.model_manager import ModelManager
from src.file_reader import FileReader
from src.config_manager import ConfigManager

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

# 注意：config_manager.load_config() 会将配置加载到环境变量中
# qwen-flash模型会在需要时通过ModelManager加载


# ==================== Pydantic模型定义 ====================

class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    message: str
    timestamp: str


class ModelsResponse(BaseModel):
    """模型列表响应"""
    status: str
    models: List[str]
    count: int


class ExtractRequest(BaseModel):
    """实体抽取请求"""
    Content: str = Field(..., description="待处理的文本，格式：地址信息 人名 电话")
    model: Optional[str] = Field(
        default="qwen-flash",
        description="模型名称（可选）"
    )
    schema: Optional[Dict[str, Any]] = Field(None, description="实体抽取schema，指定要抽取的实体类型（qwen-flash模型不使用此参数）")


class ExtractResponse(BaseModel):
    """实体抽取响应"""
    EBusinessID: str = Field(..., description="业务ID")
    Data: Dict[str, Any] = Field(..., description="提取的实体数据")
    Success: bool = Field(..., description="是否成功")
    Reason: str = Field(..., description="原因说明")
    ResultCode: str = Field(..., description="结果代码")


class FileItem(BaseModel):
    """文件项"""
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="文件内容")


class BatchExtractRequest(BaseModel):
    """批量实体抽取请求"""
    files: Optional[List[FileItem]] = Field(None, description="文件内容列表")
    file_names: Optional[List[str]] = Field(None, description="文件名列表（从data目录读取）")
    model: Optional[str] = Field(
        default="nlp_structbert_siamese-uie_chinese-base",
        description="模型名称（可选）"
    )
    schema: Optional[Dict[str, Any]] = Field(None, description="实体抽取schema（可选，默认使用entity_config.json）")


class BatchExtractResponse(BaseModel):
    """批量实体抽取响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    warnings: Optional[Dict[str, Any]] = None
    timestamp: str


class ModelSwitchRequest(BaseModel):
    """模型切换请求"""
    model: str = Field(..., description="模型名称")


class ModelSwitchResponse(BaseModel):
    """模型切换响应"""
    status: str
    message: str
    model: str


class UploadResponse(BaseModel):
    """文件上传响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str


class MultipleUploadResponse(BaseModel):
    """多文件上传响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str


# ==================== API路由 ====================

@app.get("/api/health", response_model=HealthResponse, tags=["系统"])
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "NER API服务运行正常",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/models", response_model=ModelsResponse, tags=["模型"])
async def list_models():
    """获取支持的模型列表"""
    try:
        models = model_manager.list_models()
        return {
            "status": "success",
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


@app.post("/api/extract", response_model=ExtractResponse, tags=["实体抽取"])
async def extract_entities(request: ExtractRequest):
    """
    实体抽取接口
    
    从文本中抽取实体，支持多种模型和任务类型。
    
    请求格式：
    {
        "Content": "广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575",
        "model": "qwen-flash"
    }
    
    响应格式（qwen-flash模型）：
    {
        "EBusinessID": "1279441",
        "Data": {
            "ProvinceName": "广东省",
            "StreetName": "坂田街道",
            "Address": "长坑路西2巷2号202",
            "CityName": "深圳市",
            "ExpAreaName": "龙岗区",
            "Mobile": "18273778575",
            "Name": "黄大大"
        },
        "Success": true,
        "Reason": "解析成功",
        "ResultCode": "100"
    }
    """
    try:
        # 验证输入
        if not request.Content or not request.Content.strip():
            raise HTTPException(status_code=400, detail="Content字段不能为空")
        
        # 验证模型名称
        if request.model not in model_manager.SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型: {request.model}。支持的模型: {list(model_manager.SUPPORTED_MODELS.keys())}"
            )
        
        # 加载模型
        try:
            model = model_manager.load_model(request.model)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")
        
        # 执行实体抽取
        # 记录推理开始时间
        inference_start_time = time.time()
        try:
            # 对于qwen-flash模型，schema参数会被忽略
            result = model.extract_entities(request.Content, request.schema)
            
            # 记录推理结束时间并计算耗时
            inference_end_time = time.time()
            inference_duration = inference_end_time - inference_start_time
            
            # 记录推理时间到日志
            logger.info(
                f"推理时间记录 - 方法: extract_entities | "
                f"模型: {request.model} | "
                f"文本长度: {len(request.Content)} | "
                f"推理耗时: {inference_duration:.4f}秒 ({inference_duration*1000:.2f}毫秒) | "
                f"状态: 成功"
            )
            
            # qwen-flash模型直接返回统一格式
            if request.model == 'qwen-flash':
                return result
            else:
                # 其他模型保持原有格式，但需要转换为统一格式
                # 这里为了兼容，暂时返回原有格式，但建议统一使用qwen-flash格式
                return {
                    "EBusinessID": "1279441",
                    "Data": {
                        "ProvinceName": "",
                        "StreetName": "",
                        "Address": "",
                        "CityName": "",
                        "ExpAreaName": "",
                        "Mobile": "",
                        "Name": "",
                        "entities": result.get("entities", {}),
                        "text": result.get("text", request.Content)
                    },
                    "Success": "error" not in result,
                    "Reason": result.get("error", "解析成功") if "error" in result else "解析成功",
                    "ResultCode": "100" if "error" not in result else "103"
                }
            
        except Exception as e:
            # 记录推理结束时间并计算耗时（即使失败也记录）
            inference_end_time = time.time()
            inference_duration = inference_end_time - inference_start_time
            
            # 记录推理时间到日志（失败情况）
            logger.error(
                f"推理时间记录 - 方法: extract_entities | "
                f"模型: {request.model} | "
                f"文本长度: {len(request.Content)} | "
                f"推理耗时: {inference_duration:.4f}秒 ({inference_duration*1000:.2f}毫秒) | "
                f"状态: 失败 | "
                f"错误: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=f"实体抽取失败: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/batch/extract", response_model=BatchExtractResponse, tags=["实体抽取"])
async def batch_extract_entities(request: BatchExtractRequest):
    """
    批量实体抽取接口
    
    支持两种方式：
    1. 使用files字段：直接提供文件内容列表
    2. 使用file_names字段：从data目录读取文件
    """
    try:
        # 获取文件内容字典
        files_content = {}
        read_errors = []
        
        # 方式1: 直接提供文件内容列表
        if request.files:
            for file_item in request.files:
                files_content[file_item.filename] = file_item.content
        
        # 方式2: 提供文件名列表，从data目录读取
        elif request.file_names:
            data_dir = Path(project_root) / config_manager.get_data_dir()
            
            if not data_dir.exists():
                raise HTTPException(status_code=400, detail=f"数据目录不存在: {data_dir}")
            
            for filename in request.file_names:
                file_path = data_dir / filename
                try:
                    content = file_reader.read_file(str(file_path))
                    files_content[filename] = content
                except Exception as e:
                    read_errors.append({"filename": filename, "error": str(e)})
            
            # 如果所有文件都读取失败，返回错误
            if not files_content and read_errors:
                raise HTTPException(
                    status_code=400,
                    detail="所有文件读取失败",
                    headers={"errors": str(read_errors)}
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="请提供files字段（文件内容列表）或file_names字段（文件名列表）"
            )
        
        if not files_content:
            raise HTTPException(status_code=400, detail="没有有效的文件内容需要处理")
        
        # 获取schema（可选，默认使用entity_config.json）
        schema = request.schema
        if not schema:
            try:
                schema = config_manager.load_entity_config()
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"schema字段为空且无法加载默认配置: {str(e)}"
                )
        
        # 验证模型名称
        if request.model not in model_manager.SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型: {request.model}。支持的模型: {list(model_manager.SUPPORTED_MODELS.keys())}"
            )
        
        # 加载模型
        try:
            model = model_manager.load_model(request.model)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")
        
        # 执行批量实体抽取
        # 记录推理开始时间
        inference_start_time = time.time()
        try:
            results = model.extract_from_files(files_content, schema)
            
            # 记录推理结束时间并计算耗时
            inference_end_time = time.time()
            inference_duration = inference_end_time - inference_start_time
            
            # 记录推理时间到日志
            total_text_length = sum(len(content) for content in files_content.values())
            logger.info(
                f"推理时间记录 - 方法: extract_from_files | "
                f"模型: {request.model} | "
                f"文件数量: {len(files_content)} | "
                f"总文本长度: {total_text_length} | "
                f"推理耗时: {inference_duration:.4f}秒 ({inference_duration*1000:.2f}毫秒) | "
                f"平均每文件耗时: {inference_duration/len(files_content):.4f}秒 | "
                f"状态: 成功"
            )
            
            # 检查结果中是否有错误
            has_error = False
            error_files = []
            for filename, result in results.items():
                if "error" in result:
                    has_error = True
                    error_files.append(filename)
            
            # 准备返回数据
            response_data = {
                "status": "success",
                "data": {
                    "files_count": len(results),
                    "results": results,
                    "model": request.model,
                    "schema": schema
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # 添加警告信息
            warnings = {}
            if read_errors:
                warnings["read_errors"] = read_errors
                warnings["message"] = f"{len(read_errors)} 个文件读取失败"
            
            if has_error:
                if "message" in warnings:
                    warnings["message"] += f", {len(error_files)} 个文件处理失败"
                else:
                    warnings["message"] = f"{len(error_files)} 个文件处理失败"
                warnings["error_files"] = error_files
            
            if warnings:
                response_data["warnings"] = warnings
            
            return response_data
            
        except Exception as e:
            # 记录推理结束时间并计算耗时（即使失败也记录）
            inference_end_time = time.time()
            inference_duration = inference_end_time - inference_start_time
            
            # 记录推理时间到日志（失败情况）
            total_text_length = sum(len(content) for content in files_content.values())
            logger.error(
                f"推理时间记录 - 方法: extract_from_files | "
                f"模型: {request.model} | "
                f"文件数量: {len(files_content)} | "
                f"总文本长度: {total_text_length} | "
                f"推理耗时: {inference_duration:.4f}秒 ({inference_duration*1000:.2f}毫秒) | "
                f"状态: 失败 | "
                f"错误: {str(e)}"
            )
            raise HTTPException(status_code=500, detail=f"批量实体抽取失败: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/model/switch", response_model=ModelSwitchResponse, tags=["模型"])
async def switch_model(request: ModelSwitchRequest):
    """切换模型接口（预加载模型）"""
    try:
        # 验证模型名称
        if request.model not in model_manager.SUPPORTED_MODELS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的模型: {request.model}。支持的模型: {list(model_manager.SUPPORTED_MODELS.keys())}"
            )
        
        # 加载模型
        try:
            model = model_manager.load_model(request.model)
            return {
                "status": "success",
                "message": f"模型切换成功: {request.model}",
                "model": request.model
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/upload", response_model=UploadResponse, tags=["文件管理"])
async def upload_file(
    file: UploadFile = File(..., description="要上传的文件"),
    overwrite: bool = Form(True, description="如果文件已存在是否覆盖（默认true）")
):
    """
    文件上传接口
    
    支持的文件格式: .txt, .md, .docx, .doc, .pdf
    默认保留原文件名，如果文件已存在则覆盖（除非overwrite=false）
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="文件名为空")
        
        # 验证文件格式
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in file_reader.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式: {file_ext}。支持的格式: {file_reader.SUPPORTED_EXTENSIONS}"
            )
        
        # 获取data目录路径
        data_dir = Path(project_root) / config_manager.get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建保存路径（保留原文件名）
        save_filename = file.filename
        save_path = data_dir / save_filename
        
        # 检查文件是否已存在
        if save_path.exists() and not overwrite:
            raise HTTPException(
                status_code=400,
                detail=f"文件已存在: {save_filename}，且overwrite=false不允许覆盖。请设置overwrite=true或删除已存在的文件"
            )
        
        overwritten = save_path.exists() and overwrite
        
        # 保存文件
        try:
            with open(save_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            file_size = save_path.stat().st_size
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件保存失败: {str(e)}")
        
        # 返回成功结果
        return {
            "status": "success",
            "data": {
                "filename": save_filename,
                "original_filename": file.filename,
                "file_path": str(save_path.relative_to(project_root)),
                "file_size": file_size,
                "overwritten": overwritten
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


@app.post("/api/upload/multiple", response_model=MultipleUploadResponse, tags=["文件管理"])
async def upload_multiple_files(
    files: List[UploadFile] = File(..., description="要上传的文件列表（可上传多个）"),
    overwrite: bool = Form(True, description="如果文件已存在是否覆盖（默认true）")
):
    """
    多文件上传接口
    
    支持的文件格式: .txt, .md, .docx, .doc, .pdf
    默认保留原文件名，如果文件已存在则覆盖（除非overwrite=false）
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="文件列表为空")
        
        # 获取data目录路径
        data_dir = Path(project_root) / config_manager.get_data_dir()
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # 处理所有文件
        results = []
        success_count = 0
        failed_count = 0
        
        for file in files:
            if not file.filename:
                continue
            
            file_ext = Path(file.filename).suffix.lower()
            
            # 验证文件格式
            if file_ext not in file_reader.SUPPORTED_EXTENSIONS:
                results.append({
                    "filename": file.filename,
                    "original_filename": file.filename,
                    "status": "error",
                    "error": f"不支持的文件格式: {file_ext}"
                })
                failed_count += 1
                continue
            
            # 构建保存路径（保留原文件名）
            save_filename = file.filename
            save_path = data_dir / save_filename
            
            # 检查文件是否已存在
            if save_path.exists() and not overwrite:
                results.append({
                    "filename": file.filename,
                    "original_filename": file.filename,
                    "status": "error",
                    "error": "文件已存在，且overwrite=false不允许覆盖。请设置overwrite=true或删除已存在的文件"
                })
                failed_count += 1
                continue
            
            overwritten = save_path.exists() and overwrite
            
            # 保存文件
            try:
                with open(save_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                file_size = save_path.stat().st_size
                
                results.append({
                    "filename": save_filename,
                    "original_filename": file.filename,
                    "file_path": str(save_path.relative_to(project_root)),
                    "file_size": file_size,
                    "overwritten": overwritten,
                    "status": "success"
                })
                success_count += 1
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "original_filename": file.filename,
                    "status": "error",
                    "error": f"文件保存失败: {str(e)}"
                })
                failed_count += 1
        
        # 返回结果
        return {
            "status": "success",
            "data": {
                "success_count": success_count,
                "failed_count": failed_count,
                "files": results
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("NER Demo API服务启动 (FastAPI)")
    print("=" * 60)
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