# 物联网 PDF 手册 RAG（Ollama + LlamaIndex + Chroma）

用本地大模型对物联网设备手册做检索增强问答，全离线、无需 API Key。

> **部署位置（C 盘零残留）**
> - 应用与向量库：`D:\on premises deployment\iot_rag\`
> - Python 环境：`D:\on premises deployment\.venv\`
> - Ollama 模型：`D:\on premises deployment\ollama-models\`（由环境变量 `OLLAMA_MODELS` 指定）
> - Ollama 程序本体：`D:\on premises deployment\ollama-app\`（约 2.8GB）
> - 部署总览见 `D:\on premises deployment\README.md`

## 技术栈

| 组件 | 选型 | 说明 |
|---|---|---|
| 本地模型服务 | Ollama 0.40.4 | Windows 安装版 |
| 对话模型 | `qwen2:7b` (Q4_0, 4.4GB) | 生成回答 |
| 向量模型 | `bge-m3` (1.2GB) | 中文/多语言检索，**强制跑 CPU** |
| RAG 框架 | LlamaIndex 0.14 | 切分、检索、问答编排 |
| 向量库 | ChromaDB 1.5（本地持久化） | `iot_rag/storage/chroma/` |
| PDF 解析 | pypdf + llama-index-readers-file | |

## 目录结构

```
D:\on premises deployment\
├── ollama-app\                    # Ollama 程序本体（2.8GB）
├── .venv\                         # Python 虚拟环境（3.13）
├── ollama-models\                 # Ollama 模型库（blobs / manifests，5.3GB）
│   ├── blobs\
│   └── manifests\
├── start_ollama.bat               # 一键启动 Ollama 服务（带推荐参数）
├── README.md                      # 部署总说明
└── iot_rag\
    ├── data\iot_gateway_manual.pdf    # 导入语料（示例手册，可替换成你自己的 PDF）
    ├── storage\chroma\                # 向量库持久化目录
    ├── make_sample_manual.py          # 生成示例手册 PDF
    ├── rag.py                         # 主脚本：build / ask / chat
    ├── test_qa.py                     # 问答测试集
    └── README.md
```

## 使用

```bash
# 0. 前提：Ollama 服务在运行
#    推荐直接双击 D:\on premises deployment\start_ollama.bat
#    （它会自动带上 OLLAMA_MODELS / 双模型驻留等推荐参数）

cd "D:\on premises deployment\iot_rag"

# 1. 建库（把 data/ 下的 PDF 切分、向量化、写入 Chroma）
..\.venv\Scripts\python.exe rag.py build

# 2. 单次提问
..\.venv\Scripts\python.exe rag.py ask "CO2 传感器的量程和精度是多少？"
..\.venv\Scripts\python.exe rag.py ask "RS485 接反了怎么办？" -k 6   # 调整召回条数

# 3. 交互问答
..\.venv\Scripts\python.exe rag.py chat

# 4. 回归测试
..\.venv\Scripts\python.exe test_qa.py
```

换成自己的手册：把 PDF 丢进 `data/`（可删掉示例），重跑 `rag.py build` 即可。

> 注：`.venv\Scripts\` 下的第三方命令行小工具（`pip.exe` 除外）内部仍记录着迁移前的旧路径，
> 如需使用请改用 `python -m <模块>` 形式（例如 `python -m pip`、`python -m uvicorn`）。

## 环境变量（当前已固化）

| 变量 | 值 | 作用 |
|---|---|---|
| `OLLAMA_MODELS` | `D:\on premises deployment\ollama-models` | 模型库位置，迁出 C 盘 |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | 让 qwen2 与 bge-m3 同时驻留，避免反复重载 |
| `OLLAMA_KEEP_ALIVE` | `30m` | 模型常驻时长 |

> `OLLAMA_MODELS` 与 `OLLAMA_MAX_LOADED_MODELS` 已在用户级环境变量中固化；
> `OLLAMA_KEEP_ALIVE` 由 `start_ollama.bat` 在启动时设置。

## 关键调优记录（踩坑点）

1. **PDF 被当成二进制向量化**
   只装 `llama-index` 不会带 PDF 解析器，`SimpleDirectoryReader` 会退化成按字节读，
   检索出来的全是 `%PDF-1.4 ... endstream`。
   → 必须装 `llama-index-readers-file`；`rag.py` 里已加文本校验，解析失败会直接报错退出。

2. **6GB 显存装不下两个模型，导致每题卡几十秒**
   qwen2:7b 占 4.3GB 显存，bge-m3 若也上显存，总量超过可用的 5.0GB，
   Ollama 判定超限后会反复卸载/重载模型（每次重载 7~15 秒），生成速度掉到 3 tok/s。
   → 给向量模型加 `ollama_additional_kwargs={"num_gpu": 0}` 强制走 CPU
   （单条 query 向量化仅 ~200ms，完全够快），LLM 独占显存。

3. **只允许 1 个模型驻留**
   Ollama 默认 `OLLAMA_MAX_LOADED_MODELS=1`，检索和生成会互相把对方踢出内存。
   → 设置为 2，并加长 `OLLAMA_KEEP_ALIVE`。

4. **上下文开太大反而更慢**
   `num_ctx=32768` 时 KV cache 撑爆显存，36% 的层被迫回退 CPU。
   → 固定在 `num_ctx=4096`（检索 4 个块足够放），模型完整驻留显存。

5. **中文回答要靠提示词约束**
   LlamaIndex 默认 QA 模板是英文，qwen2 容易用英文答。
   → `rag.py` 里换成中文模板，并要求"资料没有就回答资料中未提及"，抑制幻觉。

6. **Windows 上模型文件与虚拟环境都不该放在 C 盘**
   模型 5.2GB + venv 0.6GB 全部迁到 D 盘；venv 迁移后 `python.exe`/`pip` 仍可用，
   但 `Scripts\*.exe` 的 console script 需重建或改用 `python -m` 形式。

## 实测性能（RTX 3060 Laptop 6GB + i7-12700H + 16GB）

- 生成速度：**45~48 tok/s**（热态，num_ctx=4096）
- 单次问答端到端：**1~6 秒**（首问含模型预热约 13 秒）
- 冷启动首次加载模型：约 25~40 秒
- 手册切分为 9 个向量块
- 迁移后复测（模型从 D 盘加载）：8 题全对，耗时 0.8~5.5 秒
