# NER Demo

基于ModelScope SiameseUIE模型的中文命名实体识别（NER）演示程序。

## 功能特性

- ✅ 支持多种文件格式：TXT、MD、WORD、PDF
- ✅ 支持多个ModelScope模型进行实体抽取：
  - SiameseUIE模型：支持NER、关系抽取、事件抽取、属性情感抽取
  - MacBERT模型：支持命名实体识别
  - MGeo地理组成分析模型：支持地理实体识别和地理组成分析
- ✅ 支持多种信息抽取任务：
  - 命名实体识别（NER）
  - 关系抽取
  - 事件抽取
  - 属性情感抽取
  - 地理组成分析
- ✅ **文本预处理功能**：使用qwen-flash大模型进行地址错字纠错和补全，支持单条和批量处理
- ✅ 通过JSON配置文件自定义实体类型和抽取任务
- ✅ 环境配置管理（开发/生产环境）
- ✅ 自动识别环境（基于域名）
- ✅ 结果输出为JSON格式
- ✅ 完善的错误处理和日志记录
- ✅ **FastAPI RESTful API服务**：提供HTTP接口，支持批量处理、文件上传等功能
- ✅ **文本预处理接口**：地址错字纠错和信息补全，保留人名和电话，支持单条和批量处理
- ✅ **自动API文档**：Swagger UI和ReDoc交互式文档

## 项目结构

```
NER_demo/
├── data/                  # 输入数据文件夹
├── output/                # 输出结果文件夹
├── model/                 # 模型文件夹
│   ├── nlp_structbert_siamese-uie_chinese-base/
│   ├── chinese-macbert-base/
│   └── mgeo_geographic_composition_analysis_chinese_base/
├── src/                   # 源代码文件夹
│   ├── config_manager.py  # 配置管理模块
│   ├── file_reader.py     # 文件读取模块
│   ├── siamese_uie_model.py  # SiameseUIE模型调用模块
│   ├── macbert_model.py      # MacBERT模型调用模块
│   ├── mgeo_geographic_composition_analysis_chinese_base_model.py  # MGeo地理组成分析模型调用模块
│   ├── text_preprocessor.py  # 文本预处理模块（地址纠错和补全）
│   └── main.py            # 主程序入口
├── entity_config.json     # 实体配置文件
├── app.py                # FastAPI API服务主程序
├── requirements.txt       # Python依赖
├── start.py              # Windows启动脚本（命令行模式）
├── start.sh              # Linux启动脚本（命令行模式）
├── test/                  # 测试脚本目录
│   └── test_model_load.py # 模型加载测试脚本
└── README.md             # 项目说明文档
```

## 安装步骤

### 1. 安装依赖

**重要提示：** 本项目对依赖版本有严格要求，请确保按照以下步骤安装：

```bash
pip install -r requirements.txt
```

**关键依赖版本说明：**
- `transformers>=4.40.0,<4.49.0` - 必须在此版本范围内，避免兼容性问题
- `accelerate>=0.20.0` - 必需，用于模型初始化
- `tokenizers>=0.15.0` - 预编译版本，无需Rust编译

如果遇到模型加载失败的问题，请参考"常见问题"部分。

### 2. 配置环境

复制 `.env.template` 为 `.env` 并修改配置：

```bash
# Windows
copy .env.template .env

# Linux/Mac
cp .env.template .env
```

**注意**: 如果 `.env.template` 文件不存在，请参考 `SETUP.md` 文件手动创建 `.env` 文件。

编辑 `.env` 文件，配置以下内容：

```env
# 环境类型: dev_env 或 show_env
ENV_TYPE=dev_env

# 开发环境域名列表（用逗号分隔）
DEV_DOMAINS=localhost,127.0.0.1,dev.example.com

# 生产环境域名列表（用逗号分隔）
SHOW_DOMAINS=prod.example.com,www.example.com

# 模型路径（相对于项目根目录）
MODEL_PATH=model/nlp_structbert_siamese-uie_chinese-base

# 数据文件夹路径
DATA_DIR=data

# 输出文件夹路径
OUTPUT_DIR=output

# 实体配置文件路径
ENTITY_CONFIG_PATH=entity_config.json

# 模型是否已下载（true/false）
MODEL_DOWNLOADED=true

# DashScope API密钥（用于文本预处理功能，qwen-flash模型）
# 获取方式：https://dashscope.console.aliyun.com/apiKey
# 如果不使用文本预处理功能，可以留空
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 配置实体类型

编辑 `entity_config.json` 文件，设置需要抽取的实体类型和任务类型。

#### 命名实体识别（NER）配置示例：

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

#### 关系抽取配置示例：

```json
{
  "entities": {
    "人物": {
      "比赛项目(赛事名称)": null,
      "参赛地点(城市)": null,
      "获奖时间(时间)": null,
      "选手国籍(国籍)": null
    }
  },
  "description": "关系抽取配置"
}
```

#### 事件抽取配置示例：

```json
{
  "entities": {
    "胜负(事件触发词)": {
      "时间": null,
      "败者": null,
      "胜者": null,
      "赛事名称": null
    }
  },
  "description": "事件抽取配置"
}
```

#### MGeo地理组成分析模型说明：

**重要**：MGeo模型使用token-classification任务，**不需要schema配置**。

- MGeo模型会自动识别地址中的各个成分（省份、城市、区县、街道、POI等）
- 在API调用时，`schema`参数可以为空或任意值，模型会忽略此参数
- 直接输入地址文本即可，例如："浙江省杭州市余杭区阿里巴巴西溪园区"

更多配置示例请参考模型目录下的 `README.md` 文件。

## 使用方法

本项目提供两种使用方式：

### 方式1：API服务模式（推荐）

使用 FastAPI 提供的 RESTful API 接口，支持批量处理和文件上传。

#### 1. 启动API服务

```bash
python app.py
```

服务启动后，默认运行在：`http://localhost:8000`

#### 2. 访问API文档

FastAPI 自动生成了交互式API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 3. 使用API接口

详见 `QUICKSTART.md` 文件了解详细的API使用方法。

### 方式2：命令行模式（已废弃）

> ⚠️ **注意**: 命令行模式已废弃，不再自动处理data目录下的文件。推荐使用API服务模式。

**Windows系统：**
```bash
python start.py
```

**Linux/Mac系统：**
```bash
chmod +x start.sh
./start.sh
```

或者直接运行：
```bash
python -m src.main
```

### 查看结果

- **API模式**：结果直接通过API返回
- **命令行模式**：结果保存在 `output/` 文件夹下，文件名为 `ner_results_YYYYMMDD_HHMMSS.json`

## 输出格式

输出JSON文件格式如下：

```json
{
  "timestamp": "20251219_182332",
  "entity_schema": {
    "人物": null,
    "地理位置": null,
    "组织机构": null,
    "时间": null,
    "事件": null
  },
  "files_count": 1,
  "results": {
    "example.txt": {
      "text": "文件完整内容...",
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
          ]
        ]
      }
    }
  }
}
```

**输出说明：**
- `timestamp`: 处理时间戳
- `entity_schema`: 使用的实体抽取配置（MGeo模型此字段为空）
- `files_count`: 处理的文件数量
- `results`: 每个文件的抽取结果
  - `text`: 文件原始内容
  - `entities.output`: 抽取的实体列表，每个实体包含：
    - `type`: 实体类型
    - `span`: 实体文本
    - `offset`: 实体在文本中的位置 [起始位置, 结束位置]

**MGeo模型输出格式示例：**

MGeo模型的输出格式略有不同，返回地址成分列表：

```json
{
  "text": "浙江省杭州市余杭区阿里巴巴西溪园区",
  "entities": {
    "output": [
      {"type": "PB", "start": 0, "end": 3, "span": "浙江省"},
      {"type": "PC", "start": 3, "end": 6, "span": "杭州市"},
      {"type": "PD", "start": 6, "end": 9, "span": "余杭区"},
      {"type": "Entity", "start": 9, "end": 17, "span": "阿里巴巴西溪园区"}
    ]
  }
}
```

**MGeo输出字段说明：**
- `type`: 地址成分类型（PB=省, PC=城市, PD=区县, Entity=POI等）
- `start`: 成分在文本中的起始位置
- `end`: 成分在文本中的结束位置
- `span`: 成分的文本内容

## 支持的文件格式

- **TXT**: 纯文本文件
- **MD**: Markdown文件
- **WORD**: .docx 和 .doc 格式
- **PDF**: PDF文档

## 环境配置说明

程序支持两种环境：
- **dev_env**: 开发环境
- **show_env**: 生产环境

环境可以通过以下方式确定：
1. `.env` 文件中的 `ENV_TYPE` 配置
2. 自动检测：根据主机名和域名列表自动判断

## 测试

项目提供了测试脚本来验证模型加载和初始化：

```bash
python test/test_model_load.py
```

测试脚本会检查：
- 配置加载
- 模型路径和文件完整性
- 模型初始化
- 实体抽取功能

## 支持的模型

项目目前支持以下三个模型：

### 1. SiameseUIE模型 (`nlp_structbert_siamese-uie_chinese-base`)
- **用途**：通用信息抽取
- **支持任务**：命名实体识别、关系抽取、事件抽取、属性情感抽取
- **模型路径**：`model/nlp_structbert_siamese-uie_chinese-base/`

### 2. MacBERT模型 (`chinese-macbert-base`)
- **用途**：命名实体识别
- **支持任务**：命名实体识别（基于规则方法）
- **模型路径**：`model/chinese-macbert-base/`

### 3. MGeo地理组成分析模型 (`mgeo_geographic_composition_analysis_chinese_base`)
- **用途**：地理实体识别和地址成分分析
- **支持任务**：地址成分分析（Address Composition Analysis）
- **模型路径**：`model/mgeo_geographic_composition_analysis_chinese_base/`
- **适用场景**：处理地址query、行政区划、地理位置描述等文本
- **特殊说明**：
  - MGeo模型使用token-classification任务，**不需要schema参数**
  - 直接输入地址文本即可，模型会自动识别地址中的各个成分
  - 支持识别省份、城市、区县、街道、POI、品牌等多种地理实体类型
- **输出格式**：返回地址成分列表，每个成分包含类型、位置和文本内容

## 注意事项

1. **模型文件**：确保模型已下载到对应的模型目录，包含以下必要文件：
   - `config.json` 或 `configuration.json`
   - `pytorch_model.bin`
   - `vocab.txt`（如果适用）
   
   各模型目录：
   - `model/nlp_structbert_siamese-uie_chinese-base/`
   - `model/chinese-macbert-base/`
   - `model/mgeo_geographic_composition_analysis_chinese_base/`

2. **依赖版本**：请严格按照 `requirements.txt` 中的版本要求安装依赖，避免版本兼容性问题。
   - **注意**：MGeo模型可能需要特定版本的transformers，如果遇到兼容性问题，代码会自动尝试使用ModelScope模型ID加载（推荐方式）

3. **模型目录依赖**：模型目录中的 `requirements.txt` 已更新为兼容版本，请勿随意修改。
   - MGeo模型会自动优先使用ModelScope模型ID，让ModelScope处理版本兼容性

4. **首次运行**：首次运行可能需要下载模型依赖，请确保网络连接正常。

5. **处理时间**：处理大文件时可能需要较长时间，请耐心等待。

6. **PDF文件**：PDF文件读取依赖PyPDF2或pypdf库，某些复杂PDF可能无法正确解析。

7. **CUDA支持**：如果系统有CUDA支持，模型会自动使用GPU加速；否则使用CPU运行。

8. **文本预处理功能**：需要配置 `DASHSCOPE_API_KEY` 才能使用文本预处理功能。
   - 获取API Key：https://dashscope.console.aliyun.com/apiKey
   - 在 `dev.env` 或 `.env` 文件中设置 `DASHSCOPE_API_KEY=your_api_key_here`
   - 如果不使用文本预处理功能，可以留空

## 常见问题

### Q: 模型加载失败，提示 `NameError: name 'init_empty_weights' is not defined`？

A: 这是版本兼容性问题。解决方法：

1. **检查 transformers 版本**：
   ```bash
   pip show transformers
   ```
   确保版本在 `4.40.0` 到 `4.48.9` 之间。

2. **重新安装兼容版本**：
   ```bash
   pip uninstall transformers huggingface-hub tokenizers -y
   pip install transformers==4.40.0 huggingface-hub==0.25.2 accelerate
   ```

3. **检查模型目录依赖**：确保 `model/nlp_structbert_siamese-uie_chinese-base/requirements.txt` 中的版本正确。

### Q: 模型加载失败，提示 `cannot import name 'GGUF_CONFIG_MAPPING'`？

A: 这是 transformers 版本过新导致的兼容性问题。请降级到兼容版本：
```bash
pip install transformers==4.40.0
```

### Q: 安装 tokenizers 时提示需要 Rust 编译？

A: 使用预编译的 tokenizers 版本：
```bash
pip install tokenizers --only-binary :all:
```

### Q: 模型加载失败，提示模型路径不存在？

A: 
1. 检查 `dev.env` 或 `show.env` 中的 `MODEL_PATH` 配置是否正确
2. 确保模型目录存在且包含必要的模型文件
3. 路径可以是相对路径（相对于项目根目录）或绝对路径

### Q: 文件读取失败？

A: 
1. 检查文件格式是否支持（TXT、MD、WORD、PDF）
2. 检查文件是否损坏
3. 检查文件编码是否正确（建议使用UTF-8编码）

### Q: 如何选择使用哪个模型？

A: 根据任务类型选择：
- **通用信息抽取**（NER、关系抽取、事件抽取等）：使用 `nlp_structbert_siamese-uie_chinese-base`
- **简单命名实体识别**：使用 `chinese-macbert-base`
- **地址成分分析和地理实体识别**：使用 `mgeo_geographic_composition_analysis_chinese_base`

在API请求中通过 `model` 参数指定模型名称。

### Q: MGeo模型如何使用？需要schema参数吗？

A: **MGeo模型不需要schema参数**，这是与其他模型的主要区别：

1. **MGeo模型特点**：
   - 使用token-classification任务，自动识别地址中的各个成分
   - 不需要指定要抽取的实体类型
   - 直接输入地址文本即可

2. **API调用示例**：
   ```json
   {
     "text": "浙江省杭州市余杭区阿里巴巴西溪园区",
     "model": "mgeo_geographic_composition_analysis_chinese_base",
     "schema": {}
   }
   ```
   注意：`schema`参数可以为空或任意值，MGeo模型会忽略此参数。

3. **输出格式**：
   ```json
   {
     "status": "success",
     "data": {
       "text": "浙江省杭州市余杭区阿里巴巴西溪园区",
       "entities": {
         "output": [
           {"type": "PB", "start": 0, "end": 3, "span": "浙江省"},
           {"type": "PC", "start": 3, "end": 6, "span": "杭州市"},
           {"type": "PD", "start": 6, "end": 9, "span": "余杭区"},
           {"type": "Entity", "start": 9, "end": 17, "span": "阿里巴巴西溪园区"}
         ]
       }
     }
   }
   ```

4. **支持的地址成分类型**：
   - `PB`: 省
   - `PC`: 城市
   - `PD`: 区县
   - `PE`: 乡镇
   - `PF`: 街道
   - `PG`: 村庄
   - `PH`: 行政俗称/商圈
   - `Entity`: POI一般名称
   - `Brand`: 著名品牌
   - `UA/UB/UC/UD/UE`: 门址信息
   - 更多类型请参考模型README

### Q: MGeo模型加载失败，提示transformers版本兼容性问题？

A: MGeo模型可能需要特定版本的transformers。如果遇到 `No module named 'transformers.models.bert.configuration_bert'` 错误：

1. **优先方案**：使用ModelScope模型ID（推荐）
   - 代码会自动尝试使用ModelScope模型ID加载，让ModelScope处理版本兼容性
   - 首次使用会自动下载模型到缓存目录

2. **备选方案**：降级transformers版本
   ```bash
   pip install transformers==4.20.1
   ```
   注意：降级transformers可能影响其他模型，请谨慎操作。

3. **参考文档**：查看模型README了解详细版本要求
   ```
   model/mgeo_geographic_composition_analysis_chinese_base/README.md
   ```

### Q: 实体抽取结果为空？

A: 
1. **对于SiameseUIE和MacBERT模型**：
   - 检查 `entity_config.json` 配置是否正确
   - 检查文本内容是否包含相关实体
   - 尝试调整实体类型名称，使用更通用的名称
   - 查看输出文件中的 `entities` 字段，确认是否有错误信息

2. **对于MGeo模型**：
   - 确保输入的是地址相关的文本（如"浙江省杭州市余杭区"）
   - MGeo模型会自动识别地址成分，不需要配置schema
   - 如果结果为空，可能是文本不包含有效的地理信息
   - 查看输出中的 `error` 字段，确认是否有错误信息

### Q: 如何测试模型是否正常工作？

A: 运行测试脚本：
```bash
python test/test_model_load.py
```

### Q: 支持哪些信息抽取任务？

A: 本项目支持以下任务类型：

**SiameseUIE模型支持的任务：**
- **命名实体识别（NER）**：`{"实体类型": null}`
- **关系抽取**：`{"主语实体": {"关系(宾语实体)": null}}`
- **事件抽取**：`{"事件类型(触发词)": {"参数类型": null}}`
- **属性情感抽取**：`{"属性词": {"情感词": null}}`

**MGeo模型支持的任务：**
- **地址成分分析**：不需要schema参数，直接输入地址文本即可
  - 自动识别地址中的省份、城市、区县、街道、POI等成分
  - 适用于地址解析、地理实体识别等场景

**文本预处理功能：**
- **地址纠错和补全**：使用qwen-flash大模型对地址信息进行处理
  - **单条处理**（向后兼容）：
    - 请求格式：`{"Content": "地址信息 人名 电话"}`
    - 返回格式：`{"Content": "处理后的地址信息 人名 电话"}`
  - **批量处理**（新功能）：
    - 请求格式：`{"Content": ["地址信息1 人名1 电话1", "地址信息2 人名2 电话2", ...]}`
    - 返回格式：`{"Content": ["处理后的地址信息1 人名1 电话1", "处理后的地址信息2 人名2 电话2", ...]}`
  - 只处理地址部分，保留人名和电话不变
  - 地址补全格式：省份、城市、区县、街道、详细地址
  - 接口会自动识别输入格式（字符串或数组），返回格式与输入格式一致

详细配置示例请参考模型目录下的 `README.md` 文件。

## 许可证

本项目使用 Apache License 2.0 许可证。

