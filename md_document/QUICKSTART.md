# NER Demo API 快速开始

## 功能概述

NER Demo API 提供了基于FastAPI的RESTful接口，支持：
- ✅ 前端传入文本和模型选择
- ✅ 后端调用指定模型进行推理
- ✅ 返回JSON格式的抽取结果
- ✅ 支持两个模型：`chinese-macbert-base` 和 `nlp_structbert_siamese-uie_chinese-base`

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动API服务

```bash
python app.py
```

服务启动后，默认运行在：`http://localhost:8000`

### 3. 测试API

#### 方式1：使用自动生成的API文档（推荐）

FastAPI 自动生成了交互式 API 文档，可以直接在浏览器中测试：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

在文档页面中可以直接测试所有API接口，无需额外工具。

#### 方式2：使用Postman

1. 打开Postman
2. 导入 `postman_collection.json` 文件（注意：需要将端口从5000改为8000）
3. 选择任意请求进行测试

#### 方式3：使用测试脚本

```bash
python test/test_api.py
```

#### 方式4：使用curl

```bash
# 健康检查
curl http://localhost:8000/api/health

# 获取模型列表
curl http://localhost:8000/api/models

# 实体抽取
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
    "model": "nlp_structbert_siamese-uie_chinese-base",
    "schema": {
      "人物": null,
      "地理位置": null,
      "组织机构": null
    }
  }'
```

## API接口说明

### 主要接口：实体抽取

**接口地址：** `POST /api/extract`

**请求示例：**
```json
{
  "text": "待处理的文本",
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": {
    "人物": null,
    "地理位置": null,
    "组织机构": null
  }
}
```

**响应示例：**
```json
{
  "status": "success",
  "data": {
    "text": "原始文本",
    "entities": {
      "output": [
        [
          {
            "type": "人物",
            "span": "谷口清太郎",
            "offset": [18, 23]
          }
        ]
      ]
    },
    "model": "nlp_structbert_siamese-uie_chinese-base"
  },
  "timestamp": "2025-01-19T10:30:00.123456"
}
```

### 其他接口

- `GET /api/health` - 健康检查
- `GET /api/models` - 获取支持的模型列表
- `POST /api/model/switch` - 切换/预加载模型
- `POST /api/batch/extract` - 批量实体抽取
- `POST /api/upload` - 文件上传（单个文件）
- `POST /api/upload/multiple` - 文件上传（多个文件）

> 💡 **提示**: 所有接口的详细文档、请求/响应格式和示例都可以在 FastAPI 自动生成的文档页面查看：http://localhost:8000/docs

## 支持的模型

1. **nlp_structbert_siamese-uie_chinese-base**（推荐）
   - 专门用于信息抽取任务
   - 支持命名实体识别、关系抽取、事件抽取等

2. **chinese-macbert-base**
   - BERT基础模型
   - 需要确认是否支持SiameseUIE pipeline

## 注意事项

1. **首次加载模型**：首次使用某个模型时，需要加载模型到内存，可能需要几秒到几十秒的时间。

2. **模型路径**：确保模型文件已正确下载到 `model/` 目录下。

3. **内存占用**：每个模型会占用一定的内存，如果内存有限，建议只使用一个模型。

4. **API文档**：访问 http://localhost:8000/docs 查看完整的交互式API文档
5. **FastAPI优势**：自动生成API文档、类型验证、更好的性能、支持异步处理

## 常见问题

### Q: 模型加载失败？

A: 检查模型文件是否存在于 `model/` 目录下，确保包含必要的模型文件。

### Q: 如何切换模型？

A: 在请求中指定 `model` 字段，或者在首次请求时指定，模型会自动加载并缓存。

### Q: 支持哪些实体类型？

A: 支持自定义实体类型，通过 `schema` 字段指定。支持命名实体识别、关系抽取、事件抽取等多种任务。

## 下一步

- 查看 `API_DOC.md` 了解完整的API文档
- 导入 `postman_collection.json` 到Postman进行测试
- 运行 `python test/test_api.py` 进行自动化测试

