# -*- coding: utf-8 -*-
"""受控实验：定位生成速度两极分化（3 t/s vs 44 t/s）的原因"""
import json
import subprocess
import urllib.request

API = "http://127.0.0.1:11434"
PROXY = {"http": None, "https": None}
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def post(path, payload, timeout=300):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(req, timeout=timeout) as r:
        return json.load(r)


def ps():
    with opener.open(API + "/api/ps", timeout=30) as r:
        return json.load(r)


def vram():
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used,memory.free", "--format=csv,noheader"],
        capture_output=True, text=True,
    ).stdout.strip()
    return out


def gen(tag, n=120):
    d = post("/api/chat", {
        "model": "qwen2:7b",
        "messages": [{"role": "user", "content": "请从1数到40，用逗号分隔，不要解释。"}],
        "stream": False,
        "options": {"num_ctx": 4096, "num_predict": n, "temperature": 0.1},
    })
    ec = d["eval_count"]
    ed = d["eval_duration"] / 1e9
    pe = d["prompt_eval_duration"] / 1e9
    print(f"  [{tag}] 生成 {ec} tok / {ed:.2f}s = {ec/ed:6.1f} tok/s | 提示 {pe:.2f}s | 显存 {vram()}")
    return ec / ed


print("=== A. 当前状态（bge-m3 与 qwen2 同时驻留）===")
for m in ps()["models"]:
    print(f"  {m['name']}: 显存 {m.get('size_vram',0)/1e9:.2f} GB / 总 {m['size']/1e9:.2f} GB")
for i in range(2):
    gen(f"A{i+1}")

print("\n=== B. 卸载全部模型后，只跑 LLM ===")
post("/api/generate", {"model": "qwen2:7b", "keep_alive": 0})
post("/api/generate", {"model": "bge-m3", "keep_alive": 0})
import time
time.sleep(3)
for i in range(3):
    gen(f"B{i+1}")

print("\n=== C. 加载 bge-m3（CPU）后再跑 LLM ===")
post("/api/embed", {"model": "bge-m3", "input": "预热", "keep_alive": "30m",
                    "options": {"num_gpu": 0}})
time.sleep(2)
for m in ps()["models"]:
    print(f"  {m['name']}: 显存 {m.get('size_vram',0)/1e9:.2f} GB / 总 {m['size']/1e9:.2f} GB")
for i in range(3):
    gen(f"C{i+1}")
