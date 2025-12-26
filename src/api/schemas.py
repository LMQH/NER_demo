"""
API 请求和响应的 Pydantic 模型定义
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


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

