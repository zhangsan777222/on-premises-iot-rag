# -*- coding: utf-8 -*-
"""对比：短提示 vs 长提示（模拟 RAG 的 4 个召回块）下的生成速度"""
import json
import urllib.request

API = "http://127.0.0.1:11434"
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def chat(prompt, n=120, ctx=4096):
    req = urllib.request.Request(
        API + "/api/chat",
        data=json.dumps({
            "model": "qwen2:7b",
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {"num_ctx": ctx, "num_predict": n, "temperature": 0.1},
        }).encode(),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(req, timeout=600) as r:
        d = json.load(r)
    ec, ed = d["eval_count"], d["eval_duration"] / 1e9
    pe, pc = d.get("prompt_eval_duration", 0) / 1e9, d.get("prompt_eval_count", 0)
    print(f"  ctx={ctx:5d} 提示{pc:5d}tok/{pe:5.2f}s  生成{ec:4d}tok/{ed:5.2f}s = {ec/ed:6.1f} tok/s")
    return ec / ed


short = "请从1数到40，用逗号分隔，不要解释。"
long_ctx = "以下是参考资料：\n" + ("物联网网关支持 MQTT、Modbus RTU、HTTP 上报；供电 DC 9~36V；" * 60) + "\n问题：请从1数到40，用逗号分隔，不要解释。"

print("=== 短提示 ===")
chat(short)
print("=== 长提示（约 1500 token 上下文）===")
chat(long_ctx)
chat(long_ctx)
print("=== 长提示 + 更大 num_ctx(8192) ===")
chat(long_ctx, ctx=8192)
