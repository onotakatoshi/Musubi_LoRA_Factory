from __future__ import annotations

import subprocess


def query_nvidia_smi() -> str:
    cmd = [
        "nvidia-smi",
        "--query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw,power.limit",
        "--format=csv,noheader,nounits",
    ]
    try:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=10)
    except FileNotFoundError:
        return "nvidia-smi が見つかりません。NVIDIA driver / PATH を確認してください。"
    except subprocess.TimeoutExpired:
        return "nvidia-smi がタイムアウトしました。"

    if proc.returncode != 0:
        return "nvidia-smi の実行に失敗しました。\n\n" + (proc.stdout or "")

    rows = []
    for line in proc.stdout.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 8:
            continue
        idx, name, temp, util, mem_used, mem_total, power, power_limit = parts[:8]
        try:
            mem_pct = float(mem_used) / float(mem_total) * 100 if float(mem_total) else 0
        except ValueError:
            mem_pct = 0
        rows.append(
            {
                "index": idx,
                "name": name,
                "temp": temp,
                "util": util,
                "mem_used": mem_used,
                "mem_total": mem_total,
                "mem_pct": mem_pct,
                "power": power,
                "power_limit": power_limit,
            }
        )

    if not rows:
        return "GPU情報を取得できませんでした。"

    lines = ["# GPU Status", ""]
    for gpu in rows:
        lines.append(f"## GPU {gpu['index']}: {gpu['name']}")
        lines.append(f"- Temperature: {gpu['temp']} °C")
        lines.append(f"- Utilization: {gpu['util']} %")
        lines.append(f"- Memory: {gpu['mem_used']} / {gpu['mem_total']} MiB ({gpu['mem_pct']:.1f}%)")
        lines.append(f"- Power: {gpu['power']} / {gpu['power_limit']} W")
        lines.append("")
    return "\n".join(lines)


def gpu_preflight_warning() -> str:
    status = query_nvidia_smi()
    if "nvidia-smi" in status and "見つかりません" in status:
        return status
    warnings = []
    for line in status.splitlines():
        if "Memory:" in line:
            # line example: - Memory: 1000 / 24000 MiB (4.2%)
            if "(" in line and "%" in line:
                try:
                    pct = float(line.split("(")[-1].split("%")[-2])
                    if pct > 85:
                        warnings.append("GPUメモリ使用率が高いです。学習開始前に他プロセスを確認してください。")
                except ValueError:
                    pass
    if warnings:
        return status + "\n\n## Warning\n" + "\n".join(f"- {w}" for w in warnings)
    return status
