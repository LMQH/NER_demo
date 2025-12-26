# NER Demo API 使用文档

## 概述

NER Demo API 提供了基于FastAPI的RESTful接口，支持前端传入文本和模型选择进行命名实体识别（NER）任务。

**支持的模型（共5个）：**
- `qwen-flash` - Qwen-Flash大模型，通过API调用进行地址实体抽取（推荐，默认模型）
- `chinese-macbert-base` - MacBERT基础模型，支持命名实体识别
- `nlp_structbert_siamese-uie_chinese-base` - SiameseUIE通用信息抽取模型，支持NER、关系抽取、事件抽取、属性情感抽取
- `mgeo_geographic_composition_analysis_chinese_base` - MGeo地理组成分析模型，支持地理实体识别和地理组成分析
- `mgeo_geographic_elements_tagging_chinese_base` - MGeo地理要素标注模型，支持地理要素标注和地址成分识别

**功能特性：**
- ✅ 自动记录推理时间并写入日志文件
- ✅ 支持单条实体抽取
- ✅ 自动API文档（Swagger UI和ReDoc）
- ✅ 完善的错误处理和日志记录

## 启动服务

### 方式1：直接运行
```bash
python app.py
```

服务启动后，默认运行在：`http://localhost:8000`

**注意：** 本文档中的端口号为8000（FastAPI默认端口），如果您的服务运行在其他端口，请相应调整URL。

## 日志记录

系统会自动记录每个方法调用的推理时间到日志文件：

- **日志位置**：`logs/inference_YYYYMMDD.log`（项目根目录下的logs文件夹）
- **日志格式**：`YYYY-MM-DD HH:MM:SS - NER_API - LEVEL - 消息内容`
- **记录内容**：推理方法、模型名称、文本长度、推理耗时、执行状态等
- **输出位置**：同时输出到日志文件和控制台

**日志示例：**
```
2023-12-21 15:30:45 - NER_API - INFO - 推理时间记录 - 方法: extract_entities | 模型: qwen-flash | 文本长度: 50 | 推理耗时: 1.2345秒 (1234.50毫秒) | 状态: 成功
```

## API接口列表

### 1. 健康检查

**接口地址：** `GET /api/health`

**说明：** 检查API服务是否正常运行

**请求示例：**
```bash
curl http://localhost:8000/api/health
```

**响应示例：**
```json
{
  "status": "ok",
  "message": "NER API服务运行正常",
  "timestamp": "2025-01-19T10:30:00.123456"
}
```

---

### 2. 获取支持的模型列表

**接口地址：** `GET /api/models`

**说明：** 获取当前支持的模型列表

**请求示例：**
```bash
curl http://localhost:8000/api/models
```

**响应示例：**
```json
{
  "status": "success",
  "models": [
    "chinese-macbert-base",
    "nlp_structbert_siamese-uie_chinese-base",
    "mgeo_geographic_composition_analysis_chinese_base",
    "mgeo_geographic_elements_tagging_chinese_base",
    "qwen-flash"
  ],
  "count": 5
}
```

---

### 3. 实体抽取（主要接口）

**接口地址：** `POST /api/extract`

**说明：** 对传入的文本进行实体抽取，支持多种模型和任务类型。系统会自动记录推理时间到日志文件。

**请求头：**
```
Content-Type: application/json
```

**请求体（JSON）：**

**qwen-flash模型请求格式：**
```json
{
  "Content": "广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575",
  "model": "qwen-flash"
}
```

**其他模型请求格式：**
```json
{
  "Content": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": {
    "人物": null,
    "地理位置": null,
    "组织机构": null
  }
}
```

**请求参数说明：**
- `Content` (必需): 待处理的文本内容
  - **qwen-flash模型**：格式为 `地址信息 人名 电话`，例如：`"广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575"`
  - **其他模型**：任意文本内容
- `model` (可选): 模型名称，默认为 `qwen-flash`
  - 可选值：
    - `qwen-flash` - Qwen-Flash大模型，通过API调用进行地址实体抽取（推荐，默认）
    - `chinese-macbert-base` - MacBERT基础模型，支持命名实体识别
    - `nlp_structbert_siamese-uie_chinese-base` - SiameseUIE通用信息抽取模型，支持NER、关系抽取、事件抽取、属性情感抽取
    - `mgeo_geographic_composition_analysis_chinese_base` - MGeo地理组成分析模型，支持地理实体识别和地理组成分析
    - `mgeo_geographic_elements_tagging_chinese_base` - MGeo地理要素标注模型，支持地理要素标注和地址成分识别
- `schema` (可选): 实体抽取配置，定义要抽取的实体类型（qwen-flash模型不使用此参数，会被忽略）
  - 命名实体识别格式：`{"实体类型": null}`
  - 关系抽取格式：`{"主语实体": {"关系(宾语实体)": null}}`
  - 事件抽取格式：`{"事件类型(触发词)": {"参数类型": null}}`
  - 地理组成分析格式：`{"地理实体": null, "地理位置": null, "地理组成": null}`

**请求示例（curl）：**

**qwen-flash模型：**
```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "Content": "广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575",
    "model": "qwen-flash"
  }'
```

**其他模型：**
```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "Content": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
    "model": "nlp_structbert_siamese-uie_chinese-base",
    "schema": {
      "人物": null,
      "地理位置": null,
      "组织机构": null
    }
  }'
```

**响应示例（qwen-flash模型 - 成功）：**
```json
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
```

**响应示例（其他模型 - 成功）：**
```json
{
  "EBusinessID": "1279441",
  "Data": {
    "ProvinceName": "",
    "StreetName": "",
    "Address": "",
    "CityName": "",
    "ExpAreaName": "",
    "Mobile": "",
    "Name": "",
    "entities": {
      "output": [
        [
          {
            "type": "人物",
            "span": "谷口清太郎",
            "offset": [18, 23]
          }
        ],
        [
          {
            "type": "地理位置",
            "span": "日本",
            "offset": [26, 28]
          }
        ],
        [
          {
            "type": "组织机构",
            "span": "北大",
            "offset": [6, 8]
          }
        ]
      ]
    },
    "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。"
  },
  "Success": true,
  "Reason": "解析成功",
  "ResultCode": "100"
}
```

**响应示例（错误）：**
```json
{
  "detail": "Content字段不能为空"
}
```

**HTTP状态码：**
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

**注意事项：**
1. qwen-flash模型不需要schema参数，会自动识别地址、人名、电话
2. 系统会自动记录推理时间到日志文件（`logs/inference_YYYYMMDD.log`）
3. qwen-flash模型需要配置 `DASHSCOPE_API_KEY` 环境变量

---

## Schema配置说明

### 命名实体识别（NER）

抽取独立的实体类型：

```json
{
  "人物": null,
  "地理位置": null,
  "组织机构": null,
  "时间": null,
  "事件": null
}
```

### 关系抽取

抽取实体之间的关系：

```json
{
  "人物": {
    "比赛项目(赛事名称)": null,
    "参赛地点(城市)": null,
    "获奖时间(时间)": null,
    "选手国籍(国籍)": null
  }
}
```

### 事件抽取

抽取事件及其参数：

```json
{
  "胜负(事件触发词)": {
    "时间": null,
    "败者": null,
    "胜者": null,
    "赛事名称": null
  }
}
```

### 属性情感抽取

抽取属性及其情感：

```json
{
  "属性词": {
    "情感词": null
  }
}
```

### 地理组成分析（MGeo模型）

**重要：** MGeo模型使用token-classification任务，**不需要schema配置**。在API调用时，schema参数可以为空或任意值，模型会忽略此参数。

```json
{
  "地理实体": null,
  "地理位置": null,
  "地理组成": null
}
```

**说明：** 
- `地理实体`: 识别文本中的地理实体，如城市、省份、国家等
- `地理位置`: 识别地理位置信息
- `地理组成`: 分析地理组成关系，如"中国由34个省级行政区组成"

---

## 模型说明

### 1. Qwen-Flash模型 (`qwen-flash`)

- **用途**：地址实体抽取，通过API调用进行地址信息识别和补全
- **特点**：
  - 不需要本地模型文件，通过DashScope API调用
  - 自动识别地址、人名、电话信息
  - 返回统一格式的结构化数据
  - 支持地址纠错和补全
- **输入格式**：`地址信息 人名 电话`（例如：`"广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575"`）
- **输出格式**：统一的JSON格式，包含省份、城市、区县、街道、详细地址、人名、电话
- **配置要求**：需要配置 `DASHSCOPE_API_KEY` 环境变量
- **适用场景**：地址信息提取、快递地址解析等

### 2. SiameseUIE模型 (`nlp_structbert_siamese-uie_chinese-base`)

- **用途**：通用信息抽取
- **支持任务**：命名实体识别、关系抽取、事件抽取、属性情感抽取
- **模型路径**：`model/nlp_structbert_siamese-uie_chinese-base/`
- **适用场景**：通用文本信息抽取任务

### 3. MacBERT模型 (`chinese-macbert-base`)

- **用途**：命名实体识别
- **支持任务**：命名实体识别（基于规则方法）
- **模型路径**：`model/chinese-macbert-base/`
- **适用场景**：简单命名实体识别任务

### 4. MGeo地理组成分析模型 (`mgeo_geographic_composition_analysis_chinese_base`)

- **用途**：地理实体识别和地址成分分析
- **支持任务**：地址成分分析（Address Composition Analysis）
- **模型路径**：`model/mgeo_geographic_composition_analysis_chinese_base/`
- **适用场景**：处理地址query、行政区划、地理位置描述等文本
- **特殊说明**：
  - MGeo模型使用token-classification任务，**不需要schema参数**
  - 直接输入地址文本即可，模型会自动识别地址中的各个成分
  - 支持识别省份、城市、区县、街道、POI、品牌等多种地理实体类型

### 5. MGeo地理要素标注模型 (`mgeo_geographic_elements_tagging_chinese_base`)

- **用途**：地理要素标注和地址成分识别
- **支持任务**：地址结构化要素解析（Address Structured Elements Parsing）
- **模型路径**：`model/mgeo_geographic_elements_tagging_chinese_base/`
- **适用场景**：处理门址地址结构化要素解析、地理实体识别等任务
- **特殊说明**：
  - MGeo模型使用token-classification任务，**不需要schema参数**
  - 直接输入地址文本即可，模型会自动识别地址中的结构化要素
  - 支持识别地址中的各种地理要素和结构化信息

---

## 错误处理

API使用标准的HTTP状态码和JSON错误响应：

### 400 Bad Request
请求参数错误，例如：
- `Content`字段为空
- `schema`字段为空（对于需要schema的模型）
- 不支持的模型名称
- 文件名为空
- 不支持的文件格式

### 500 Internal Server Error
服务器内部错误，例如：
- 模型加载失败
- 实体抽取过程出错
- 文件保存失败

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

---

## 日志记录功能

系统会自动记录每个方法调用的推理时间到日志文件：

### 日志文件位置
- **目录**：`logs/`（项目根目录下）
- **文件名格式**：`inference_YYYYMMDD.log`（按日期命名）
- **示例**：`inference_20231221.log`

### 日志格式
```
YYYY-MM-DD HH:MM:SS - NER_API - LEVEL - 消息内容
```

### 记录内容

#### extract_entities方法（单文本抽取）

**成功记录（INFO级别）：**
```
推理时间记录 - 方法: extract_entities | 模型: qwen-flash | 文本长度: 50 | 推理耗时: 1.2345秒 (1234.50毫秒) | 状态: 成功
```

**失败记录（ERROR级别）：**
```
推理时间记录 - 方法: extract_entities | 模型: qwen-flash | 文本长度: 50 | 推理耗时: 0.5000秒 (500.00毫秒) | 状态: 失败 | 错误: xxx
```

### 日志输出
- **文件输出**：写入日志文件（`logs/inference_YYYYMMDD.log`）
- **控制台输出**：同时输出到控制台
- **编码**：UTF-8

### 注意事项
1. 日志文件按日期自动创建，每天一个文件
2. 即使推理失败也会记录推理时间
3. 日志文件不会自动清理，需要手动管理
4. 日志文件已添加到 `.gitignore`，不会提交到版本控制

---

## 注意事项

1. **模型加载时间**：首次使用某个模型时，需要加载模型到内存，可能需要几秒到几十秒的时间。模型加载后会缓存，后续请求会更快。

2. **内存占用**：每个模型会占用一定的内存，如果内存有限，建议只使用一个模型。

3. **并发处理**：当前版本为单线程处理，如需支持高并发，建议使用生产级WSGI服务器（如gunicorn）。

4. **模型路径**：确保模型文件已正确下载到对应的模型目录（qwen-flash除外，它使用API调用）。

5. **文本长度**：建议单次处理的文本长度不超过模型的最大输入长度限制。

6. **qwen-flash模型配置**：需要配置 `DASHSCOPE_API_KEY` 环境变量才能使用qwen-flash模型。
   - 获取API Key：https://dashscope.console.aliyun.com/apiKey
   - 在环境配置文件中设置 `DASHSCOPE_API_KEY=your_api_key_here`

7. **日志记录**：系统会自动记录推理时间到日志文件，无需额外配置。

---

## 生产环境部署建议

### 使用Gunicorn

```bash
pip install gunicorn uvicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app:app
```

### 使用Docker（可选）

创建 `Dockerfile`：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app:app"]
```

---

## 示例代码

### Python示例

```python
import requests

# API基础URL
BASE_URL = "http://localhost:8000"

# 实体抽取 - qwen-flash模型
response = requests.post(
    f"{BASE_URL}/api/extract",
    json={
        "Content": "广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575",
        "model": "qwen-flash"
    }
)
result = response.json()
print(result)

# 实体抽取 - 其他模型
response = requests.post(
    f"{BASE_URL}/api/extract",
    json={
        "Content": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
        "model": "nlp_structbert_siamese-uie_chinese-base",
        "schema": {
            "人物": None,
            "地理位置": None,
            "组织机构": None
        }
    }
)
result = response.json()
print(result)
```

### JavaScript示例

```javascript
// 使用fetch API - qwen-flash模型
fetch('http://localhost:8000/api/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    Content: '广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575',
    model: 'qwen-flash'
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));

// 使用fetch API - 其他模型
fetch('http://localhost:8000/api/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    Content: '1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。',
    model: 'nlp_structbert_siamese-uie_chinese-base',
    schema: {
      '人物': null,
      '地理位置': null,
      '组织机构': null
    }
  })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));
```

---

## API文档访问

FastAPI 自动生成了交互式API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

建议使用这些交互式文档来测试API接口。
