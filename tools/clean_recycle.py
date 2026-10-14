# -*- coding: utf-8 -*-
"""精确清理回收站中属于本次迁移的条目（解析 $I 元数据文件还原原始路径）。"""
import os
import struct
import sys
import shutil
from pathlib import Path

KEYWORDS = (r".ollama\models", r"githubRAGskill\iot_rag", r"githubRAGskill\.venv")


def parse_i(path: Path):
    """解析 $I 元数据文件，返回 (原始路径, 大小)。"""
    try:
        data = path.read_bytes()
    except Exception:
        return None
    if len(data) < 28:
        return None
    ver = struct.unpack_from("<Q", data, 0)[0]
    size = struct.unpack_from("<q", data, 8)[0]
    if ver == 2:
        plen = struct.unpack_from("<i", data, 24)[0]
        raw = data[28:28 + (plen - 1) * 2]
    else:
        plen = struct.unpack_from("<i", data, 24)[0]
        raw = data[28:28 + (plen - 1) * 2] if plen > 0 else b""
    try:
        orig = raw.decode("utf-16-le")
    except Exception:
        orig = raw.decode("utf-16-le", "replace")
    return orig, size


def main():
    drives = ["C:", "D:"]
    total_freed = 0
    for drv in drives:
        rb = Path(drv + "\\$Recycle.Bin")
        if not rb.exists():
            continue
        print(f"=== {drv} 回收站 ===")
        any_hit = False
        try:
            sids = list(rb.iterdir())
        except PermissionError:
            print("  无权限读取")
            continue
        for sid in sids:
            if not sid.is_dir():
                continue
            try:
                entries = list(sid.iterdir())
            except PermissionError:
                continue
            for item in entries:
                if not item.name.startswith("$I"):
                    continue
                parsed = parse_i(item)
                if not parsed:
                    continue
                orig, size = parsed
                if any(k.lower() in orig.lower() for k in KEYWORDS):
                    any_hit = True
                    rfile = item.parent / ("$R" + item.name[2:])
                    print(f"  命中: {orig}")
                    print(f"        大小 {size/1e9:.3f} GB | 数据项 {rfile.name}")
                    # 删除数据项
                    try:
                        if rfile.is_dir():
                            shutil.rmtree(rfile)
                        elif rfile.exists():
                            rfile.unlink()
                    except Exception as e:
                        print(f"        数据删除失败: {e}")
                        continue
                    try:
                        item.unlink()
                    except Exception as e:
                        print(f"        元数据删除失败: {e}")
                    total_freed += max(size, 0)
        if not any_hit:
            print("  无本次迁移相关条目")
    print(f"\n=== 共释放约 {total_freed/1e9:.2f} GB ===")


if __name__ == "__main__":
    main()
