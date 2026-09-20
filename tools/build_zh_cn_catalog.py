#!/usr/bin/env python3
"""Build a complete Simplified-Chinese ProxMenux catalog from English.

This helper is deliberately offline at runtime: it is only a contributor tool.
The generated JSON is the static catalog shipped by ProxMenux, so hosts never
send UI strings to a translation service.  It batches requests to the same
public Google endpoint used by the upstream automation, preserves ProxMenux
placeholders and emits English for a failed batch; the application fallback
therefore remains correct and a later run can safely refresh just failures.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


PLACEHOLDER_RE = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")
SPLIT_RE = re.compile(r"\n<<<PMXSEG_(\d+)>>>\n")
TECHNICAL_TERMS = (
    "ProxMenux Monitor", "ProxMenux", "Proxmox Backup Server", "Proxmox VE",
    "Tailscale", "Secure Gateway", "Home Assistant", "NVIDIA", "AMD", "Intel",
    "IOMMU", "SR-IOV", "VFIO", "DKMS", "SMART", "ZFS ARC", "ZFS", "LXC",
    "VM", "QEMU", "PCIe", "GPU", "TPU", "Ceph", "Borg", "PBS", "API",
    "TOTP", "SSH", "TLS", "SSL", "NVMe", "iSCSI", "NFS", "CIFS", "Samba",
    "VirtIO", "UEFI", "GRUB", "APT", "Debian", "Linux", "Docker", "LVM",
)


def flatten(node: dict, prefix: str = "") -> dict[str, str]:
    result: dict[str, str] = {}
    for key, value in node.items():
        path = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            result.update(flatten(value, path))
        else:
            result[path] = "" if value is None else str(value)
    return result


def unflatten(flat: dict[str, str]) -> dict:
    result: dict = {}
    for path, value in flat.items():
        cursor = result
        *parents, leaf = path.split(".")
        for parent in parents:
            cursor = cursor.setdefault(parent, {})
        cursor[leaf] = value
    return result


def protect(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def replace(match: re.Match[str]) -> str:
        protected.append(match.group(0))
        return f"PMXPH{len(protected) - 1}X"

    text = PLACEHOLDER_RE.sub(replace, text)
    for term in TECHNICAL_TERMS:
        if term in text:
            protected.append(term)
            text = text.replace(term, f"PMXTERM{len(protected) - 1}X")
    return text, protected


def restore(text: str, protected: list[str]) -> str:
    for index, value in enumerate(protected):
        text = text.replace(f"PMXPH{index}X", value).replace(f"PMXTERM{index}X", value)
    return text


def translate_batch(texts: list[str], timeout: int) -> list[str] | None:
    payload = ""
    for index, text in enumerate(texts):
        payload += text
        if index != len(texts) - 1:
            payload += f"\n<<<PMXSEG_{index}>>>\n"
    query = urllib.parse.urlencode({
        "client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": payload,
    })
    url = "https://translate.googleapis.com/translate_a/single?" + query
    # Explicitly keep the approved HTTP(S) proxy but ignore ALL_PROXY, whose
    # SOCKS scheme is intentionally unsupported by urllib in this environment.
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({"https": proxy} if proxy else {}))
    try:
        with opener.open(url, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    translated = "".join(part[0] for part in data[0])
    parts = SPLIT_RE.split(translated)
    if len(texts) == 1:
        return [translated]
    if len(parts) != 2 * len(texts) - 1:
        return None
    output = [parts[0]]
    for expected, value in zip(range(len(texts) - 1), parts[1::2], strict=True):
        if value != str(expected):
            return None
    output.extend(parts[2::2])
    return output


def batches(items: list[tuple[str, str]], max_chars: int) -> list[list[tuple[str, str]]]:
    output: list[list[tuple[str, str]]] = []
    current: list[tuple[str, str]] = []
    size = 0
    for item in items:
        proposed = size + len(item[1]) + 32
        if current and proposed > max_chars:
            output.append(current)
            current, size = [], 0
        current.append(item)
        size += len(item[1]) + 32
    if current:
        output.append(current)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--flat", action="store_true", help="Source and output are flat string-to-string maps (CLI/TUI catalogs).")
    parser.add_argument("--max-chars", type=int, default=3600)
    parser.add_argument("--timeout", type=int, default=45)
    parser.add_argument("--sleep", type=float, default=0.15)
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    source_flat = source if args.flat else flatten(source)
    existing_flat: dict[str, str] = {}
    if args.output.exists():
        existing = json.loads(args.output.read_text(encoding="utf-8"))
        existing_flat = existing if args.flat else flatten(existing)
    pending = [(key, value) for key, value in source_flat.items() if not existing_flat.get(key)]
    if args.limit:
        pending = pending[:args.limit]
    print(f"Source keys: {len(source_flat)}; pending: {len(pending)}", flush=True)
    for batch_no, batch in enumerate(batches(pending, args.max_chars), start=1):
        protected = [protect(value) for _, value in batch]
        translated = translate_batch([value for value, _ in protected], args.timeout)
        if translated is None:
            print(f"[{batch_no}] request failed; retaining English for {len(batch)} strings", flush=True)
            translated = [value for _, value in batch]
        for (key, source_text), target_text, (_, tokens) in zip(batch, translated, protected, strict=True):
            existing_flat[key] = restore(target_text, tokens)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output_data = existing_flat if args.flat else unflatten(existing_flat)
        args.output.write_text(json.dumps(output_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"[{batch_no}] wrote {len(existing_flat)}/{len(source_flat)} keys", flush=True)
        time.sleep(args.sleep)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
