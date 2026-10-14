# -*- coding: utf-8 -*-
"""
最简 RAG：Ollama(qwen2:7b) + LlamaIndex + Chroma + 物联网 PDF 手册

第一步 建库:  python rag.py build
第二步 提问:  python rag.py ask "CO2 传感器的量程是多少？"
交互问答:     python rag.py chat

环境变量可覆盖：LLM_MODEL / EMBED_MODEL / OLLAMA_BASE_URL
"""
import os
import sys
import argparse
from pathlib import Path

import chromadb
from llama_index.core import (
    Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex, PromptTemplate,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

BASE = Path(__file__).resolve().parent
DATA_DIR = BASE / "data"
CHROMA_DIR = BASE / "storage" / "chroma"
COLLECTION = "iot_manual"

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2:7b")
# 中文手册建议用 bge-m3（多语言、中文检索效果好）；如已装 nomic-embed-text 也可切换
EMBED_MODEL = os.getenv("EMBED_MODEL", "bge-m3")
OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# 中文问答模板：强制只用检索到的资料作答，避免模型编造
QA_TEMPLATE = PromptTemplate(
    "下面是参考资料：\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "请严格依据上述参考资料回答问题，不要编造资料中不存在的内容。\n"
    "如果参考资料中没有相关信息，请直接回答“资料中未提及”。\n"
    "请使用中文作答，需要时用条目分点说明。\n\n"
    "问题：{query_str}\n"
    "回答："
)


def check_ollama():
    """确认本地 Ollama 服务可用，并给出可操作的提示。"""
    import urllib.request
    import urllib.error

    try:
        with urllib.request.urlopen(f"{OLLAMA_BASE}/", timeout=5):
            return
    except Exception:
        pass
    sys.exit(
        f"[!] 连不上 Ollama 服务（{OLLAMA_BASE}）。\n"
        "    请先启动服务，任选一种：\n"
        "      1) 双击 D:\\on premises deployment\\start_ollama.bat （推荐）\n"
        "      2) 开始菜单运行 Ollama\n"
        "      3) 命令行执行 ollama serve\n"
        "    如提示模型找不到，请确认环境变量：\n"
        "      OLLAMA_MODELS = D:\\on premises deployment\\ollama-models"
    )


def setup_settings():
    """统一配置 LLM / 向量模型 / 切分器，保证建库与查询一致。"""
    Settings.llm = Ollama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE,
        request_timeout=180.0,
        # num_ctx 控制在 4096：KV cache 小，才能把模型完整放进 6GB 显存，避免回退 CPU 变慢
        additional_kwargs={"num_ctx": 4096, "num_predict": 512, "temperature": 0.1},
    )
    # 关键：bge-m3 强制走 CPU（num_gpu=0）。显卡只有 6GB，
    # 若向量模型也占显存，会和 qwen2:7b 互抢导致 Ollama 反复卸载/重载模型（每题卡到几十秒）。
    Settings.embed_model = OllamaEmbedding(
        model_name=EMBED_MODEL,
        base_url=OLLAMA_BASE,
        ollama_additional_kwargs={"num_gpu": 0},
    )
    # 手册为中文，1 个 token≈1.5 汉字，chunk_size 512 约 700 字，重叠 64 保上下文连续
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)
    Settings.context_window = 4096
    Settings.num_output = 512


def get_collection(create=False):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    if create:
        try:
            client.delete_collection(COLLECTION)  # 重建时清空旧库
        except Exception:
            pass
    return client.get_or_create_collection(COLLECTION)


def build():
    """读取 data/*.pdf -> 切分 -> 向量化 -> 写入 Chroma。"""
    setup_settings()
    if not DATA_DIR.exists() or not any(DATA_DIR.glob("*.pdf")):
        sys.exit(f"[!] 未找到 PDF，请把手册放到 {DATA_DIR}")

    print(f"[1/3] 读取 PDF：{DATA_DIR}")
    docs = SimpleDirectoryReader(
        input_dir=str(DATA_DIR), required_exts=[".pdf"]
    ).load_data()
    print(f"      共 {len(docs)} 页/文档")

    # 校验：确认真的解析出文本，而不是把 PDF 二进制当文本塞进来
    sample = docs[0].text[:2000]
    if "%PDF-" in sample or "endstream" in sample:
        sys.exit(
            "[!] PDF 文本解析失败（拿到的是原始二进制）。\n"
            "    请确认已安装: pip install llama-index-readers-file"
        )
    print(f"      预览: {docs[0].text[:60].strip()!r}")

    print(f"[2/3] 向量化并写入 Chroma：{CHROMA_DIR}")
    collection = get_collection(create=True)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        docs, storage_context=storage_context, show_progress=True
    )

    print(f"[3/3] 完成，向量库集合 `{COLLECTION}` 共 {collection.count()} 条向量")


def get_query_engine(top_k=4):
    setup_settings()
    collection = get_collection()
    if collection.count() == 0:
        sys.exit("[!] 知识库为空，请先执行：python rag.py build")
    vector_store = ChromaVectorStore(chroma_collection=collection)
    index = VectorStoreIndex.from_vector_store(vector_store)
    return index.as_query_engine(
        similarity_top_k=top_k, text_qa_template=QA_TEMPLATE
    )


def show_sources(resp):
    print("\n--- 召回片段 ---")
    for i, node in enumerate(resp.source_nodes, 1):
        text = node.node.get_content().replace("\n", " ")
        print(f"[{i}] score={node.score:.4f}  {text[:110]}...")


def ask(question, top_k=4, show_src=True):
    engine = get_query_engine(top_k=top_k)
    resp = engine.query(question)
    print("\n=== 回答 ===")
    print(str(resp).strip())
    if show_src:
        show_sources(resp)


def chat(top_k=4):
    engine = get_query_engine(top_k=top_k)
    print("进入问答模式，输入 exit / q 退出。")
    while True:
        try:
            q = input("\nQ> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if q.lower() in ("exit", "q", "quit", ""):
            break
        resp = engine.query(q)
        print("\nA>", str(resp).strip())
        show_sources(resp)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Ollama + LlamaIndex + Chroma 最简 RAG")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="导入 PDF 建立向量知识库")
    p_ask = sub.add_parser("ask", help="单次提问")
    p_ask.add_argument("question", help="问题文本")
    p_ask.add_argument("-k", "--top-k", type=int, default=4)
    sub.add_parser("chat", help="交互式问答")
    args = ap.parse_args()

    if args.cmd == "build":
        check_ollama()
        build()
    elif args.cmd == "ask":
        check_ollama()
        ask(args.question, top_k=args.top_k)
    elif args.cmd == "chat":
        check_ollama()
        chat()
