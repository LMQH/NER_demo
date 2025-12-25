# NER Demo API

基于多种模型的中文命名实体识别（NER）和信息抽取API服务，支持Qwen-Flash、SiameseUIE、MacBERT、MGeo等多个模型，适用于地址解析、实体抽取、关系抽取等多种场景。

## 功能特性

- ✅ **多模型支持**：支持Qwen-Flash、SiameseUIE、MacBERT、MGeo等多个模型进行实体抽取
- ✅ **地址信息提取与补全**：自动识别地址、人名、电话信息，支持地址纠错和补全
- ✅ **数据库地址补全**：基于MySQL数据库的区域信息进行地址数据补全和验证
- ✅ **RESTful API服务**：基于FastAPI提供HTTP接口，支持批量处理
- ✅ **自动API文档**：Swagger UI和ReDoc交互式文档
- ✅ **完善的日志记录**：自动记录推理时间、模型信息、执行状态等
- ✅ **环境配置管理**：支持开发/生产环境配置

## 技术栈

- **框架**：FastAPI
- **模型**：Qwen-Flash、SiameseUIE、MacBERT、MGeo
- **数据库**：MySQL（用于地址补全的参考）
- **Python版本**：3.8+

## 项目结构

```
NER_demo/
├── app.py                      # FastAPI服务入口
├── src/                        # 源代码文件夹
│   ├── api/                    # API相关模块
│   │   ├── routes/             # 路由模块
│   │   │   ├── extract.py      # 实体抽取路由
│   │   │   ├── file.py         # 文件处理路由
│   │   │   └── system.py       # 系统路由
│   │   ├── schemas.py          # API数据模型
│   │   └── dependencies.py     # 依赖注入
│   ├── config/                 # 配置模块
│   │   ├── config_manager.py   # 配置管理器
│   │   ├── env_loader.py       # 环境变量加载器
│   │   └── constants.py        # 常量定义
│   ├── database/               # 数据库模块
│   │   └── db_connection.py    # 数据库连接
│   ├── models/                 # 模型模块
│   │   ├── siamese_uie_model.py
│   │   ├── macbert_model.py
│   │   ├── qwen_flash_model.py
│   │   ├── mgeo_geographic_composition_analysis_chinese_base_model.py
│   │   └── mgeo_geographic_elements_tagging_chinese_base_model.py
│   ├── processors/             # 处理模块
│   │   ├── address_completer.py  # 地址补全处理
│   │   ├── text_preprocessor.py  # 文本预处理
│   │   ├── file_reader.py        # 文件读取处理
│   │   └── converters.py         # 格式转换处理
│   ├── utils/                  # 工具模块
│   │   ├── address_parser.py   # 地址解析器
│   │   ├── entity_extractor.py # 实体提取器
│   │   └── exceptions.py       # 异常定义
│   ├── model_manager.py        # 模型管理器
│   └── main.py                 # 主程序入口（已废弃，使用app.py）
├── model/                      # 模型文件夹
├── logs/                       # 日志文件夹
├── entity_config.json          # 实体配置文件
├── requirements.txt            # Python依赖
├── dev.env                     # 开发环境配置
└── README.md                   # 项目说明文档
```

## 数据库表结构

项目使用MySQL数据库存储区域信息，用于地址补全功能。表结构如下：

### region_table（区域表）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | bigint | 主键，自增 | 主键ID |
| parent_id | bigint | 索引 | 父级编号 |
| region_name | varchar | 索引，非空 | 区域名称 |
| region_type | int | 索引，非空 | 区域类型（1001=省，1002=市，1003=区/县，1004=街道/镇） |
| alias_name | varchar | 索引 | 别名 |
| creator | varchar | 非空，默认空字符串 | 创建人 |
| creator_id | bigint | 非空，默认0 | 创建人ID |
| create_time | timestamp | 可空 | 创建时间 |
| last_operator | varchar | 非空，默认空字符串 | 最后操作人 |
| last_operator_id | bigint | 非空，默认0 | 最后操作人ID |
| last_modify_time | timestamp | 可空 | 编辑时间 |
| is_deleted | tinyint | 索引，默认0 | 是否删除（0=否，1=是） |

**区域类型说明**：
- 1001：省/直辖市/自治区
- 1002：市
- 1003：区/县
- 1004：街道/镇

## 安装步骤

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制环境变量模板文件：

```bash
# Windows
copy .env_template dev.env

# Linux/Mac
cp .env_template dev.env
```

编辑 `dev.env` 文件，配置以下内容：

```env
# DashScope API密钥（用于qwen-flash模型，必需）
DASHSCOPE_API_KEY=your_api_key_here

# MySQL数据库配置（用于地址补全功能）
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database
MYSQL_CHARSET=utf8mb4
MYSQL_REGION_TABLE=region_table

# 区域类型映射配置（可选，使用默认值）
REGION_TYPE_PROVINCE=1001
REGION_TYPE_CITY=1002
REGION_TYPE_EXP_AREA=1003
REGION_TYPE_STREET=1004

# 模型路径配置（可选）
MODEL_PATH=model/nlp_structbert_siamese-uie_chinese-base
ENTITY_CONFIG_PATH=entity_config.json
```

### 3. 配置实体类型（可选）

编辑 `entity_config.json` 文件，设置需要抽取的实体类型和任务类型：

```json
{
  "entities": {
    "人物": null,
    "地理位置": null,
    "组织机构": null,
    "时间": null,
    "事件": null
  },
  "description": "实体抽取配置，支持命名实体识别（NER）任务"
}
```

## 启动服务

### 方式1：直接运行（推荐）

```bash
python app.py
# 或者 python start.py
```

### 方式2：使用uvicorn

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后，默认运行在：`http://localhost:8000`

## API接口文档

启动服务后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API接口说明

### 1. 健康检查

**GET** `/api/health`

检查服务运行状态。

**响应示例**：
```json
{
  "status": "ok",
  "message": "NER API服务运行正常",
  "timestamp": "2025-12-25T10:00:00"
}
```

### 2. 获取支持的模型列表

**GET** `/api/models`

获取系统支持的所有模型列表。

**响应示例**：
```json
{
  "status": "success",
  "models": [
    "qwen-flash",
    "nlp_structbert_siamese-uie_chinese-base",
    "chinese-macbert-base",
    "mgeo_geographic_composition_analysis_chinese_base",
    "mgeo_geographic_elements_tagging_chinese_base"
  ],
  "count": 5
}
```

### 3. 实体抽取

**POST** `/api/extract`

从文本中抽取实体，支持多种模型。

**请求体**：
```json
{
  "Content": "广东省深圳市龙岗区坂田街道长坑路西2巷2号202 黄大大 18273778575",
  "model": "qwen-flash",
  "schema": null
}
```

**参数说明**：
- `Content`（必需）：待处理的文本，格式：地址信息 人名 电话
- `model`（可选）：模型名称，默认为 `qwen-flash`
- `schema`（可选）：实体抽取schema，指定要抽取的实体类型（qwen-flash和MGeo模型不使用此参数）

**响应示例**：
```json
{
  "EBusinessID": "1279441",
  "Data": {
    "ProvinceName": "广东省",
    "CityName": "深圳市",
    "ExpAreaName": "龙岗区",
    "StreetName": "坂田街道",
    "Address": "长坑路西2巷2号202",
    "Mobile": "18273778575",
    "Name": "黄大大"
  },
  "Success": true,
  "Reason": "解析成功",
  "ResultCode": "100"
}
```

**说明**：
- 如果配置了MySQL数据库连接，系统会自动进行地址补全
- 地址补全功能会根据数据库中的区域信息验证和补全地址数据

### 4. 批量实体抽取

**POST** `/api/batch/extract`

批量处理多个文件的实体抽取。

**请求体**：
```json
{
  "files": [
    {
      "filename": "example.txt",
      "content": "文件内容..."
    }
  ],
  "model": "nlp_structbert_siamese-uie_chinese-base",
  "schema": null
}
```

## 支持的模型

### 1. Qwen-Flash模型（推荐，默认）

- **模型标识**：`qwen-flash`
- **用途**：地址实体抽取
- **特点**：
  - 通过DashScope API调用，不需要本地模型文件
  - 自动识别地址、人名、电话信息
  - 支持地址纠错和补全
  - 返回统一格式的结构化数据
- **配置要求**：需要配置 `DASHSCOPE_API_KEY` 环境变量
- **适用场景**：地址信息提取、快递地址解析等

### 2. SiameseUIE模型

- **模型标识**：`nlp_structbert_siamese-uie_chinese-base`
- **用途**：通用信息抽取
- **支持任务**：命名实体识别、关系抽取、事件抽取、属性情感抽取
- **适用场景**：通用文本信息抽取任务

### 3. MacBERT模型

- **模型标识**：`chinese-macbert-base`
- **用途**：命名实体识别
- **支持任务**：命名实体识别（基于规则方法）
- **适用场景**：简单命名实体识别任务

### 4. MGeo地理组成分析模型

> MGeo地址Query成分分析要素识别-中文-地址领域-base

- **模型标识**：`mgeo_geographic_composition_analysis_chinese_base`
- **用途**：地理实体识别和地址成分分析
- **特点**：不需要schema参数，自动识别地址成分
- **适用场景**：地址解析、地理实体识别等

### 5. MGeo地理要素标注模型

> MGeo门址地址结构化要素解析-中文-地址领域-base

- **模型标识**：`mgeo_geographic_elements_tagging_chinese_base`
- **用途**：地理要素标注和地址成分识别
- **特点**：不需要schema参数，自动识别地址要素
- **适用场景**：地址解析、地理实体识别等

## 地址补全功能

项目支持基于MySQL数据库的地址补全功能：

1. **自动补全**：根据提取的地址信息，从数据库中查找对应的区域信息进行补全
2. **数据验证**：验证提取的地址信息是否与数据库中的标准数据一致
3. **层级查找**：支持从街道向上查找省、市、区县等上级区域信息
4. **别名支持**：支持使用别名（alias_name）进行匹配

**补全逻辑**：
- 如果StreetName存在，从StreetName开始向上查找
- 如果StreetName为空，使用Address字段匹配数据库中的区域信息
- 按层级顺序补全ProvinceName、CityName、ExpAreaName、StreetName

## 日志记录

系统自动记录以下信息到日志文件：

- 推理时间：每个方法调用的推理耗时
- 模型信息：使用的模型名称
- 文本长度：处理的文本长度
- 执行状态：成功或失败
- 错误信息：详细的错误堆栈

日志文件位置：`logs/inference_YYYYMMDD.log`（按日期命名）

## 环境变量配置

### 必需配置

- `DASHSCOPE_API_KEY`：DashScope API密钥（用于qwen-flash模型）

### MySQL数据库配置（地址补全功能）

- `MYSQL_HOST`：数据库主机（默认：localhost）
- `MYSQL_PORT`：数据库端口（默认：3306）
- `MYSQL_USER`：数据库用户名（默认：root）
- `MYSQL_PASSWORD`：数据库密码
- `MYSQL_DATABASE`：数据库名称
- `MYSQL_CHARSET`：字符集（默认：utf8mb4）
- `MYSQL_REGION_TABLE`：区域表名（默认：region_table）

### 可选配置

- `REGION_TYPE_PROVINCE`：省份类型代码（默认：1001）
- `REGION_TYPE_CITY`：城市类型代码（默认：1002）
- `REGION_TYPE_EXP_AREA`：区县类型代码（默认：1003）
- `REGION_TYPE_STREET`：街道类型代码（默认：1004）

## 常见问题

### Q: 如何获取DashScope API密钥？

A: 访问 https://dashscope.console.aliyun.com/apiKey 获取API密钥，然后在环境变量中配置 `DASHSCOPE_API_KEY`。

### Q: 数据库连接失败怎么办？

A: 检查以下配置：
1. MySQL服务是否启动
2. 数据库连接配置（主机、端口、用户名、密码）是否正确
3. 数据库是否存在
4. 用户是否有访问权限
5. 区域表（region_table）是否存在

### Q: 地址补全功能如何工作？

A: 系统会从提取的地址信息中识别省、市、区县、街道等信息，然后在数据库中查找对应的区域记录，进行数据补全和验证。如果数据库中有更准确的区域信息，会用数据库中的数据替换或补充提取的结果。

### Q: 如何选择使用哪个模型？

A: 
- **地址实体抽取**（推荐）：使用 `qwen-flash`（调用API，一步到位）
- **通用信息抽取**：使用 `nlp_structbert_siamese-uie_chinese-base`
- **简单命名实体识别**：使用 `chinese-macbert-base`
- **地址成分分析**：使用 `mgeo_geographic_composition_analysis_chinese_base` 或 `mgeo_geographic_elements_tagging_chinese_base`
- **NER任务推荐组合**：使用 MGeo地址Query成分分析要素识别 模型 + MySQL表查询补全（延迟低，效果好）

### Q: 如何测试API接口？

A: 
1. 启动服务：`python app.py `  或 `python start.py`
2. 访问 http://localhost:8000/docs 查看Swagger UI文档
3. 在文档中直接测试API接口
4. 或使用Postman、curl等工具发送HTTP请求

## 许可证

本项目使用 Apache License 2.0 许可证。

