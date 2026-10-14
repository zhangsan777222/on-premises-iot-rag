# -*- coding: utf-8 -*-
"""列出回收站全部条目及其原始路径，用于确认清理范围。"""
import struct
from pathlib import Path


def parse_i(path: Path):
    try:
        data = path.read_bytes()
    except Exception:
        return None
    if len(data) < 28:
        return None
    ver = struct.unpack_from("<Q", data, 0)[0]
    size = struct.unpack_from("<q", data, 8)[0]
    plen = struct.unpack_from("<i", data, 24)[0]
    raw = data[28:28 + (plen - 1) * 2]
    try:
        orig = raw.decode("utf-16-le")
    except Exception:
        orig = raw.decode("utf-16-le", "replace")
    return orig, size, ver


for drv in ["C:", "D:"]:
    rb = Path(drv + "\\$Recycle.Bin")
    if not rb.exists():
        continue
    print(f"===== {drv} 回收站 =====")
    rows = []
    try:
        sids = list(rb.iterdir())
    except PermissionError:
        print("  （无法读取）")
        continue
    for sid in sids:
        if not sid.is_dir():
            continue
        try:
            items = list(sid.iterdir())
        except PermissionError:
            print(f"  （跳过无权限: {sid.name}）")
            continue
        for item in items:
            if item.name.startswith("$I"):
                p = parse_i(item)
                if p:
                    orig, size, ver = p
                    rows.append((size, orig, item.name, str(sid)))
    rows.sort(reverse=True)
    total = 0
    for size, orig, name, sid in rows:
        total += max(size, 0)
        print(f"  {size/1e6:12.2f} MB  {orig}")
    print(f"  ---- 共 {len(rows)} 项，报告大小合计 {total/1e9:.2f} GB ----")
    print()
