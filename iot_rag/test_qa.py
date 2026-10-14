# -*- coding: utf-8 -*-
"""RAG 知识库问答测试集：覆盖手册细节点 + 一个手册外问题（考察拒答）"""
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rag import get_query_engine, QA_TEMPLATE  # noqa: E402

CASES = [
    ("设备支持哪些通信方式？", "以太网/4G Cat.1/Wi-Fi"),
    ("RS485 接反了会出现什么现象？怎么处理？", "数据为0或跳变→对调A/B"),
    ("MQTT 默认上报间隔是多少？可调范围是？", "60秒，10~3600秒"),
    ("NET 指示灯一直快闪是什么原因？", "无信号或SIM卡异常"),
    ("设备的供电电压范围和工作温度范围？", "DC 9~36V，-30~+70℃"),
    ("读温度的 Modbus 请求报文是什么？", "01 03 00 00 00 01 84 0A"),
    ("设备缓存能存多少条记录？", "≥72000条"),
    ("设备支持蓝牙 5.0 吗？", "资料中未提及（应拒答）"),
]

engine = get_query_engine(top_k=4)
print(f"{'='*70}\nRAG 问答测试（top_k=4, LLM=qwen2:7b, Embed=bge-m3）\n{'='*70}")

ok = 0
for i, (q, expect) in enumerate(CASES, 1):
    t0 = time.time()
    resp = engine.query(q)
    dt = time.time() - t0
    top = resp.source_nodes[0].score if resp.source_nodes else 0
    print(f"\n[{i}] Q: {q}")
    print(f"    预期要点: {expect}")
    print(f"    A: {str(resp).strip()}")
    print(f"    耗时 {dt:.1f}s | 最高召回分 {top:.4f}")
    if "资料中未提及" not in str(resp):
        ok += 1

print(f"\n{'='*70}\n完成：{len(CASES)} 题，耗时统计见上。\n{'='*70}")
