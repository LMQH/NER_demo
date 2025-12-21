"""
NER Demo FastAPI服务
提供RESTful API接口，支持前端传入文本和模型选择进行实体抽取
"""
import sys
import os
import shutil
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
    text: str = Field(..., description="待处理的文本")
    model: Optional[str] = Field(
        default="nlp_structbert_siamese-uie_chinese-base",
        description="模型名称（可选）"
    )
    schema: Dict[str, Any] = Field(..., description="实体抽取schema，指定要抽取的实体类型")


class ExtractResponse(BaseModel):
    """实体抽取响应"""
    status: str
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: str


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
    
    从文本中抽取实体，支持命名实体识别、关系抽取、事件抽取等任务。
    """
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
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"模型加载失败: {str(e)}")
        
        # 执行实体抽取
        try:
            result = model.extract_entities(request.text, request.schema)
            
            # 检查是否有错误
            if "error" in result:
                return {
                    "status": "error",
                    "message": result["error"],
                    "data": {
                        "text": result.get("text", request.text),
                        "entities": result.get("entities", {}),
                        "model": request.model
                    },
                    "timestamp": datetime.now().isoformat()
                }
            
            # 返回成功结果
            return {
                "status": "success",
                "data": {
                    "text": result.get("text", request.text),
                    "entities": result.get("entities", {}),
                    "model": request.model
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
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
        try:
            results = model.extract_from_files(files_content, schema)
            
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
    print(f"API文档: http://localhost:8000/docs")
    print(f"API文档 (ReDoc): http://localhost:8000/redoc")
    print("=" * 60)
    
    # 启动FastAPI服务
    # 默认运行在 http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)