# NER Demo

基于ModelScope SiameseUIE模型的中文命名实体识别（NER）演示程序。

## 功能特性

- ✅ 支持多种文件格式：TXT、MD、WORD、PDF
- ✅ 使用ModelScope的SiameseUIE模型进行实体抽取
- ✅ 支持多种信息抽取任务：
  - 命名实体识别（NER）
  - 关系抽取
  - 事件抽取
  - 属性情感抽取
- ✅ 通过JSON配置文件自定义实体类型和抽取任务
- ✅ 环境配置管理（开发/生产环境）
- ✅ 自动识别环境（基于域名）
- ✅ 结果输出为JSON格式
- ✅ 完善的错误处理和日志记录

## 项目结构

```
NER_demo/
├── data/                  # 输入数据文件夹
├── output/                # 输出结果文件夹
├── model/                 # 模型文件夹
│   └── nlp_structbert_siamese-uie_chinese-base/
├── src/                   # 源代码文件夹
│   ├── config_manager.py  # 配置管理模块
│   ├── file_reader.py     # 文件读取模块
│   ├── ner_model.py       # NER模型调用模块
│   └── main.py            # 主程序入口
├── entity_config.json     # 实体配置文件
├── requirements.txt       # Python依赖
├── start.py              # Windows启动脚本
├── start.sh              # Linux启动脚本
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

更多配置示例请参考模型目录下的 `README.md` 文件。

## 使用方法

### 1. 准备数据文件

将需要处理的文件（TXT、MD、WORD、PDF格式）放入 `data/` 文件夹。

### 2. 运行程序

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

### 3. 查看结果

处理完成后，结果会保存在 `output/` 文件夹下，文件名为 `ner_results_YYYYMMDD_HHMMSS.json`。

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
- `entity_schema`: 使用的实体抽取配置
- `files_count`: 处理的文件数量
- `results`: 每个文件的抽取结果
  - `text`: 文件原始内容
  - `entities.output`: 抽取的实体列表，每个实体包含：
    - `type`: 实体类型
    - `span`: 实体文本
    - `offset`: 实体在文本中的位置 [起始位置, 结束位置]

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

## 注意事项

1. **模型文件**：确保模型已下载到 `model/nlp_structbert_siamese-uie_chinese-base/` 目录，包含以下必要文件：
   - `config.json`
   - `configuration.json`
   - `pytorch_model.bin`
   - `vocab.txt`

2. **依赖版本**：请严格按照 `requirements.txt` 中的版本要求安装依赖，避免版本兼容性问题。

3. **模型目录依赖**：模型目录中的 `requirements.txt` 已更新为兼容版本，请勿随意修改。

4. **首次运行**：首次运行可能需要下载模型依赖，请确保网络连接正常。

5. **处理时间**：处理大文件时可能需要较长时间，请耐心等待。

6. **PDF文件**：PDF文件读取依赖PyPDF2或pypdf库，某些复杂PDF可能无法正确解析。

7. **CUDA支持**：如果系统有CUDA支持，模型会自动使用GPU加速；否则使用CPU运行。

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

### Q: 实体抽取结果为空？

A: 
1. 检查 `entity_config.json` 配置是否正确
2. 检查文本内容是否包含相关实体
3. 尝试调整实体类型名称，使用更通用的名称
4. 查看输出文件中的 `entities` 字段，确认是否有错误信息

### Q: 如何测试模型是否正常工作？

A: 运行测试脚本：
```bash
python test/test_model_load.py
```

### Q: 支持哪些信息抽取任务？

A: 本项目支持以下任务类型：
- **命名实体识别（NER）**：`{"实体类型": null}`
- **关系抽取**：`{"主语实体": {"关系(宾语实体)": null}}`
- **事件抽取**：`{"事件类型(触发词)": {"参数类型": null}}`
- **属性情感抽取**：`{"属性词": {"情感词": null}}`

详细配置示例请参考模型目录下的 `README.md` 文件。

## 许可证

本项目使用 Apache License 2.0 许可证。

