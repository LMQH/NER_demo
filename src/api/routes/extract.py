"""
实体抽取相关路由
"""
import time
import logging
from fastapi import APIRouter, HTTPException, Depends
from src.api.schemas import ExtractRequest, ExtractResponse, BatchExtractRequest, BatchExtractResponse
from src.api.converters import convert_mgeo_to_qwen_flash_format, convert_mgeo_tagging_to_qwen_flash_format, convert_ner_to_address_format
from src.api.dependencies import get_model_manager, get_file_reader, get_config_manager, get_address_completer

router = APIRouter()
logger = logging.getLogger("NER_API")


@router.post("/api/extract", response_model=ExtractResponse, tags=["实体抽取"])
async def extract_entities(
    request: ExtractRequest,
    model_manager=Depends(get_model_manager),
    config_manager=Depends(get_config_manager),
    address_completer=Depends(get_address_completer)
):
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
                formatted_result = result
            elif request.model == 'mgeo_geographic_composition_analysis_chinese_base':
                # mgeo地理组成分析模型需要转换为qwen-flash格式
                formatted_result = convert_mgeo_to_qwen_flash_format(result, request.Content)
            elif request.model == 'mgeo_geographic_elements_tagging_chinese_base':
                # mgeo地理要素标注模型需要转换为qwen-flash格式
                formatted_result = convert_mgeo_tagging_to_qwen_flash_format(result, request.Content)
            else:
                # macbert和siameseUIE模型需要转换为统一格式
                # 加载output_schema配置
                output_schema = None
                try:
                    entity_config = config_manager.load_entity_config()
                    if isinstance(entity_config, dict) and "output_schema" in entity_config:
                        output_schema = entity_config["output_schema"]
                except Exception as e:
                    logger.warning(f"无法加载output_schema配置: {str(e)}，将使用默认映射")
                
                # 转换为统一格式
                formatted_result = convert_ner_to_address_format(result, request.Content, output_schema)
            
            # 进行地址补全
            if address_completer:
                try:
                    formatted_result = address_completer.complete_extract_response(formatted_result)
                except Exception as e:
                    logger.warning(f"地址补全失败，返回原始结果: {str(e)}")
            
            return formatted_result
            
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


@router.post("/api/batch/extract", response_model=BatchExtractResponse, tags=["实体抽取"])
async def batch_extract_entities(
    request: BatchExtractRequest,
    model_manager=Depends(get_model_manager),
    file_reader=Depends(get_file_reader),
    config_manager=Depends(get_config_manager)
):
    """
    批量实体抽取接口
    
    使用files字段：直接提供文件内容列表
    """
    from datetime import datetime
    
    try:
        # 获取文件内容字典
        files_content = {}
        read_errors = []
        
        # 直接提供文件内容列表
        if request.files:
            for file_item in request.files:
                files_content[file_item.filename] = file_item.content
        else:
            raise HTTPException(
                status_code=400,
                detail="请提供files字段（文件内容列表）"
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

