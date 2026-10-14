# On-Premises IoT RAG — 物联网手册本地问答

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-0.40.4-orange.svg)](https://ollama.com/)

全离线本地部署的检索增强问答（RAG）系统，基于本地大模型对物联网设备手册进行智能问答。**无需任何云服务或 API Key，数据不出本机。**

> 部署原则：C 盘零残留 —— 程序、模型、Python 环境、源码全部位于 D 盘。

## 技术栈

| 组件 | 选型 | 说明 |
|---|---|---|
| 本地模型服务 | Ollama 0.40.4 | Windows 安装版 |
| 对话模型 | `qwen2:7b` (Q4_0, 4.4GB) | 生成回答 |
| 向量模型 | `bge-m3` (1.2GB) | 中文/多语言检索，强制跑 CPU |
| RAG 框架 | LlamaIndex 0.14 | 切分、检索、问答编排 |
| 向量库 | ChromaDB 1.5（本地持久化） | `iot_rag/storage/chroma/` |
| PDF 解析 | pypdf + llama-index-readers-file | |

## 目录结构

```
.
├── iot_rag/                     # RAG 应用（核心代码）
│   ├── data/                    #   语料 PDF（可替换成你自己的手册）
│   ├── storage/chroma/          #   向量库持久化（gitignore，可重建）
│   ├── rag.py                   #   主脚本 build / ask / chat
│   ├── test_qa.py               #   问答回归测试集
│   ├── make_sample_manual.py    #   生成示例手册 PDF
│   └── README.md                #   详细使用说明与调优记录
├── tools/                       # 诊断与辅助脚本
│   ├── diag_speed.py            #   生成速度基准测试
│   ├── diag_ctx.py              #   上下文窗口性能对比
│   ├── clean_recycle.py         #   清理回收站中迁移残留
│   └── list_recycle.py          #   列出回收站条目
├── start_ollama.bat             # 一键启动 Ollama 服务（带推荐参数）
├── requirements.txt             # Python 依赖
├── .gitignore                   # 排除 venv / 二进制 / 模型库 / 向量库
└── README.md                    # 本文件
```

> **未纳入版本控制的大体积目录**（需自行准备）：
> - `ollama-app/` — Ollama 程序本体（2.8GB，[官方下载](https://ollama.com/)）
> - `ollama-models/` — 模型库（qwen2:7b + bge-m3，约 5.3GB）
> - `offline-installer/` — 离线安装包
> - `reference-src/` — 参考源码仓库副本
> - `.venv/` — Python 虚拟环境

## 快速开始

### 1. 安装 Ollama 并拉取模型

```bat
:: 安装 Ollama（下载到 D 盘）
:: 从 https://ollama.com/ 下载 Windows 版，安装到 D:\on premises deployment\ollama-app

:: 拉取所需模型
ollama pull qwen2:7b
ollama pull bge-m3
```

### 2. 安装 Python 依赖

```bat
cd "D:\on premises deployment"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 启动 Ollama 服务

双击 `start_ollama.bat`（自动设置 `OLLAMA_MODELS`、`OLLAMA_MAX_LOADED_MODELS=2`、`OLLAMA_KEEP_ALIVE=30m`）。

### 4. 生成示例手册并建库

```bat
cd "D:\on premises deployment\iot_rag"
..\.venv\Scripts\python.exe make_sample_manual.py
..\.venv\Scripts\python.exe rag.py build
```

### 5. 提问

```bat
:: 单次提问
..\.venv\Scripts\python.exe rag.py ask "CO2 传感器的量程和精度是多少？"

:: 交互式问答
..\.venv\Scripts\python.exe rag.py chat

:: 回归测试
..\.venv\Scripts\python.exe test_qa.py
```

## 换成你自己的手册

1. 把你的 PDF 放进 `iot_rag/data/`（可删掉示例手册）
2. 重建向量库：`python rag.py build`

## 环境变量

| 变量 | 值 | 作用 |
|---|---|---|
| `OLLAMA_MODELS` | `D:\on premises deployment\ollama-models` | 模型库位置 |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | qwen2 与 bge-m3 同时驻留 |
| `OLLAMA_KEEP_ALIVE` | `30m` | 模型常驻时长 |

> `OLLAMA_MODELS` 与 `OLLAMA_MAX_LOADED_MODELS` 建议在用户级环境变量中固化；`OLLAMA_KEEP_ALIVE` 由 `start_ollama.bat` 在启动时设置。

## 硬件与性能

- 实测环境：RTX 3060 Laptop 6GB 显存 + i7-12700H + 16GB 内存
- 生成速度：45~48 tok/s（热态）
- 单次问答端到端：0.8~6 秒（首问含模型预热约 14 秒）
- 冷启动首次加载模型：25~40 秒（正常现象）

## 关键调优记录

详细踩坑与调优记录见 [iot_rag/README.md](iot_rag/README.md)，要点包括：

1. PDF 文本解析需安装 `llama-index-readers-file`
2. 6GB 显存下 bge-m3 强制走 CPU（`num_gpu=0`），避免与 LLM 互抢
3. `OLLAMA_MAX_LOADED_MODELS=2` 让两个模型同时驻留
4. `num_ctx=4096` 避免 KV cache 撑爆显存
5. 中文 QA 模板约束模型用中文作答、资料外问题拒答

## License

[MIT](LICENSE)
