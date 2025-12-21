# NER Demo API 使用文档

## 概述

NER Demo API 提供了基于Flask的RESTful接口，支持前端传入文本和模型选择进行命名实体识别（NER）任务。

## 启动服务

### 方式1：直接运行
```bash
python app.py
```

### 方式2：使用Flask命令
```bash
flask --app app run --host=0.0.0.0 --port=5000
```

服务启动后，默认运行在：`http://localhost:5000`

## API接口列表

### 1. 健康检查

**接口地址：** `GET /api/health`

**说明：** 检查API服务是否正常运行

**请求示例：**
```bash
curl http://localhost:5000/api/health
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
curl http://localhost:5000/api/models
```

**响应示例：**
```json
{
  "status": "success",
  "models": [
    "chinese-macbert-base",
    "nlp_structbert_siamese-uie_chinese-base"
  ],
  "count": 2
}
```

---

### 3. 实体抽取（主要接口）

**接口地址：** `POST /api/extract`

**说明：** 对传入的文本进行实体抽取

**请求头：**
```
Content-Type: application/json
```

**请求体（JSON）：**
```json
{
  "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": {
    "人物": null,
    "地理位置": null,
    "组织机构": null
  }
}
```

**请求参数说明：**
- `text` (必需): 待处理的文本内容
- `model` (可选): 模型名称，默认为 `nlp_structbert_siamese-uie_chinese-base`
  - 可选值：`chinese-macbert-base` 或 `nlp_structbert_siamese-uie_chinese-base`
- `schema` (必需): 实体抽取配置，定义要抽取的实体类型
  - 命名实体识别格式：`{"实体类型": null}`
  - 关系抽取格式：`{"主语实体": {"关系(宾语实体)": null}}`
  - 事件抽取格式：`{"事件类型(触发词)": {"参数类型": null}}`

**请求示例（curl）：**
```bash
curl -X POST http://localhost:5000/api/extract \
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

**响应示例（成功）：**
```json
{
  "status": "success",
  "data": {
    "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
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
    "model": "nlp_structbert_siamese-uie_chinese-base"
  },
  "timestamp": "2025-01-19T10:30:00.123456"
}
```

**响应示例（错误）：**
```json
{
  "status": "error",
  "message": "text字段不能为空"
}
```

**HTTP状态码：**
- `200`: 成功
- `400`: 请求参数错误
- `500`: 服务器内部错误

---

### 4. 切换模型（预加载）

**接口地址：** `POST /api/model/switch`

**说明：** 预加载指定模型（可选，模型会在首次使用时自动加载）

**请求头：**
```
Content-Type: application/json
```

**请求体（JSON）：**
```json
{
  "model": "chinese-macbert-base"
}
```

**请求示例（curl）：**
```bash
curl -X POST http://localhost:5000/api/model/switch \
  -H "Content-Type: application/json" \
  -d '{
    "model": "chinese-macbert-base"
  }'
```

**响应示例：**
```json
{
  "status": "success",
  "message": "模型切换成功: chinese-macbert-base",
  "model": "chinese-macbert-base"
}
```

---

## Postman测试示例

### 1. 健康检查

**方法：** GET  
**URL：** `http://localhost:5000/api/health`  
**Headers：** 无需特殊请求头

---

### 2. 获取模型列表

**方法：** GET  
**URL：** `http://localhost:5000/api/models`  
**Headers：** 无需特殊请求头

---

### 3. 实体抽取 - 使用默认模型

**方法：** POST  
**URL：** `http://localhost:5000/api/extract`  
**Headers：**
```
Content-Type: application/json
```

**Body（raw JSON）：**
```json
{
  "text": "在北京冬奥会自由式滑雪中，中国选手谷爱凌获得金牌。",
  "schema": {
    "人物": null,
    "地理位置": null,
    "事件": null
  }
}
```

---

### 4. 实体抽取 - 指定模型

**方法：** POST  
**URL：** `http://localhost:5000/api/extract`  
**Headers：**
```
Content-Type: application/json
```

**Body（raw JSON）：**
```json
{
  "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": {
    "人物": null,
    "地理位置": null,
    "组织机构": null,
    "时间": null
  }
}
```

---

### 5. 关系抽取示例

**方法：** POST  
**URL：** `http://localhost:5000/api/extract`  
**Headers：**
```
Content-Type: application/json
```

**Body（raw JSON）：**
```json
{
  "text": "在北京冬奥会自由式滑雪中，中国选手谷爱凌获得金牌。",
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": {
    "人物": {
      "比赛项目(赛事名称)": null,
      "参赛地点(城市)": null,
      "获奖时间(时间)": null
    }
  }
}
```

---

### 6. 切换模型

**方法：** POST  
**URL：** `http://localhost:5000/api/model/switch`  
**Headers：**
```
Content-Type: application/json
```

**Body（raw JSON）：**
```json
{
  "model": "chinese-macbert-base"
}
```

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

---

## 错误处理

API使用标准的HTTP状态码和JSON错误响应：

### 400 Bad Request
请求参数错误，例如：
- `text`字段为空
- `schema`字段为空
- 不支持的模型名称

### 500 Internal Server Error
服务器内部错误，例如：
- 模型加载失败
- 实体抽取过程出错

错误响应格式：
```json
{
  "status": "error",
  "message": "错误描述信息"
}
```

---

## 注意事项

1. **模型加载时间**：首次使用某个模型时，需要加载模型到内存，可能需要几秒到几十秒的时间。模型加载后会缓存，后续请求会更快。

2. **内存占用**：每个模型会占用一定的内存，如果内存有限，建议只使用一个模型。

3. **并发处理**：当前版本为单线程处理，如需支持高并发，建议使用生产级WSGI服务器（如gunicorn）。

4. **模型路径**：确保模型文件已正确下载到 `model/` 目录下。

5. **文本长度**：建议单次处理的文本长度不超过模型的最大输入长度限制。

---

## 生产环境部署建议

### 使用Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 使用Docker（可选）

创建 `Dockerfile`：
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 示例代码

### Python示例

```python
import requests

# API基础URL
BASE_URL = "http://localhost:5000"

# 实体抽取
response = requests.post(
    f"{BASE_URL}/api/extract",
    json={
        "text": "1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。",
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
// 使用fetch API
fetch('http://localhost:5000/api/extract', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: '1944年毕业于北大的名古屋铁道会长谷口清太郎等人在日本积极筹资。',
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

