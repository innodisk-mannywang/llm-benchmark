import json

from anyio import open_file

from type.metrics import TTFT, Latency, Token
from type.report import Report


def generate_test_report(
    model: str,
    max_tokens: int,
    num_concurrency: int,
    requests: int,
    duration: float,
    dataset: str,
    prompt: str,
    ttft_list: list[float],
    latency_list: list[float],
    token_list: list[int],
) -> Report:
    ttft = TTFT(
        avg_ttft=round(sum(ttft_list) / len(ttft_list) * 1000, 2),
        max_ttft=round(max(ttft_list) * 1000, 2),
        min_ttft=round(min(ttft_list) * 1000, 2),
    )

    latency = Latency(
        avg_latency=round(sum(latency_list) / len(latency_list), 2),
        max_latency=round(max(latency_list), 2),
        min_latency=round(min(latency_list), 2),
    )

    token = Token(
        avg_token=round(sum(token_list) / len(token_list), 2),
        max_token=max(token_list),
        min_token=min(token_list),
    )

    return Report(
        model=model,
        max_tokens=max_tokens,
        num_concurrency=num_concurrency,
        total_requests=requests,
        total_duration_time=round(duration, 2),
        dataset=dataset if dataset else prompt,
        successful_requests=len(latency_list),
        request_per_sec=round(requests / duration, 2),
        throughput_token=round(sum(token_list) / sum(latency_list), 2),
        ttft=ttft,
        latency=latency,
        token=token,
    )


async def save_report_as_file(data: Report, save_path: str) -> None:
    report_content = {
        "Model": data.model,
        "Limit output tokens": data.max_tokens,
        "Number of concurrency": data.num_concurrency,
        "Total requests": data.total_requests,
        "Duration time (s)": data.total_duration_time,
        "Dataset": data.dataset,
        "Successful requests": data.successful_requests,
        "Request per second (req/s)": data.request_per_sec,
        "Throughput token (tok/s)": data.throughput_token,
        "TTFT": {
            "Avg ttft (ms)": data.ttft.avg_ttft,
            "Max ttft (ms)": data.ttft.max_ttft,
            "Min ttft (ms)": data.ttft.min_ttft,
        },
        "Latency": {
            "Avg latency (s)": data.latency.avg_latency,
            "Max latency (s)": data.latency.max_latency,
            "Min latency (s)": data.latency.min_latency,
        },
        "Token": {
            "Avg token (tok/req)": data.token.avg_token,
            "Max token (tok/req)": data.token.max_token,
            "Min token (tok/req)": data.token.min_token,
        },
    }
    async with await open_file(save_path, "w") as f:
        encode_data = json.dumps(report_content, indent=2, ensure_ascii=True)
        await f.write(encode_data)


# ===== CV-style reporting (align with cv-benchmark/enhanced_benchmark.py) =====
def generate_cv_style_report(
    *,
    model: str,
    dataset: str,
    concurrency: int,
    total_requests: int,
    duration_s: float,
    ttft_list: list[float],
    latency_list: list[float],  # seconds per request
    token_list: list[int],
    provider: str | None = None,
    resource_stats: dict | None = None,
) -> dict:
    def avg(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    # Derive aggregates
    avg_latency_s = avg(latency_list)
    avg_latency_ms = avg_latency_s * 1000.0
    rps_total = (total_requests / duration_s) if duration_s > 0 else 0.0
    rps_per_channel = rps_total / max(concurrency, 1)

    # Use actual resource stats if available, otherwise use zeros for compatibility
    if resource_stats:
        cpu_avg = resource_stats.get("cpu_percent", {}).get("average", 0.0)
        mem_avg = resource_stats.get("memory_percent", {}).get("average", 0.0)
        gpu_avg = resource_stats.get("gpu_percent", {}).get("average", 0.0)
    else:
        cpu_avg = 0.0
        mem_avg = 0.0
        gpu_avg = 0.0

    # Tokens
    avg_tok_per_req = avg([float(x) for x in token_list]) if token_list else 0.0
    
    # TTFT (Time To First Token) - 轉換為毫秒
    avg_ttft_ms = avg(ttft_list) * 1000.0 if ttft_list else 0.0
    min_ttft_ms = min(ttft_list) * 1000.0 if ttft_list else 0.0
    max_ttft_ms = max(ttft_list) * 1000.0 if ttft_list else 0.0

    report: dict = {
        "timestamp": __import__("datetime").datetime.now().isoformat(),
        "configuration": {
            "model": model,
            "dataset": dataset,
            "concurrency": concurrency,
            "seconds": int(duration_s),
            "provider": provider or "Innodisk IPA Dept.",
        },
        "summary": {
            "total_concurrency": concurrency,
            "total_requests": total_requests,
            "total_runtime": duration_s,
        },
        "performance_metrics": {
            # In CV report, "fps" 表示每通道處理速率；於 LLM 對齊為 req/sec/chan
            "fps": {
                "average": rps_per_channel,
                "min": rps_per_channel,
                "max": rps_per_channel,
                "per_concurrency": [rps_per_channel] * max(concurrency, 1),
            },
            "latency_ms": {
                "average": avg_latency_ms,
                "min": (min(latency_list) * 1000.0) if latency_list else 0.0,
                "max": (max(latency_list) * 1000.0) if latency_list else 0.0,
                "per_concurrency": [avg_latency_ms] * max(concurrency, 1),
            },
            "throughput": {
                "average": rps_per_channel,
                "total": rps_total,
                "per_concurrency": [rps_per_channel] * max(concurrency, 1),
            },
        },
        "resource_usage": resource_stats if resource_stats else {
            "cpu_percent": {"average": cpu_avg, "max": cpu_avg, "per_channel": [cpu_avg] * max(concurrency, 1)},
            "memory_percent": {"average": mem_avg, "max": mem_avg, "per_channel": [mem_avg] * max(concurrency, 1)},
            "gpu_percent": {"average": gpu_avg, "max": gpu_avg, "per_channel": [gpu_avg] * max(concurrency, 1)},
        },
        "detection_metrics": {
            # 對齊欄位名，於 LLM 報告中放輸出統計
            "avg_tokens_per_response": {
                "average": avg_tok_per_req,
                "per_channel": [avg_tok_per_req] * max(concurrency, 1),
            }
        },
        "ttft_ms": {
            "average": avg_ttft_ms,
            "min": min_ttft_ms,
            "max": max_ttft_ms,
            "per_concurrency": [avg_ttft_ms] * max(concurrency, 1),
        },
        "efficiency_analysis": {
            "fps_per_cpu_percent": (rps_per_channel / max(cpu_avg, 1.0)),
            "fps_per_memory_percent": (rps_per_channel / max(mem_avg, 1.0)),
            "latency_efficiency": (1000.0 / max(avg_latency_ms, 1.0)),
            "resource_efficiency": (rps_per_channel / max(cpu_avg + mem_avg, 1.0)),
        },
    }
    return report


async def save_cv_style_report_as_file(data: dict, save_path: str) -> None:
    async with await open_file(save_path, "w") as f:
        encode_data = json.dumps(data, indent=2, ensure_ascii=False)
        await f.write(encode_data)


# ===== Console pretty print (CV-style) =====
def print_cv_style_report(report: dict) -> None:
    print("\n" + "=" * 80)
    print("🔍 增強版 LLM Benchmark 報告")
    print("=" * 80)

    cfg = report.get("configuration", {})
    perf = report.get("performance_metrics", {})
    resu = report.get("resource_usage", {})
    det = report.get("detection_metrics", {})

    # 重新計算 LLM 專用指標
    total_requests = report.get("summary", {}).get("total_requests", 0)
    total_runtime = report.get("summary", {}).get("total_runtime", 1)
    concurrency = cfg.get("concurrency", 1)

    print("\n📊 測試配置:")
    print(f"  • 模型: {cfg.get('model', 'unknown')}")
    print(f"  • 資料集/提示: {cfg.get('dataset', 'prompt')}")
    print(f"  • 總請求數: {total_requests}")
    print(f"  • 併發連線數: {cfg.get('concurrency', 1)}")
    print(f"  • 執行時間: {cfg.get('seconds', 0)} 秒")
    print(f"  • Provider: {cfg.get('provider', 'Innodisk IPA Dept.')}")
    
    rps_total = total_requests / total_runtime if total_runtime > 0 else 0
    rps_per_connection = rps_total / concurrency if concurrency > 0 else 0
    
    lat = perf.get("latency_ms", {})
    thr = perf.get("throughput", {})

    print("\n⚡ 性能指標:")
    print(f"  • 總請求速率: {rps_total:.2f} req/s")
    print(f"  • 每連線速率: {rps_per_connection:.2f} req/s")
    print(f"  • 平均延遲: {lat.get('average', 0):.2f} ms")
    print(f"  • 延遲範圍: {lat.get('min', 0):.2f} - {lat.get('max', 0):.2f} ms")
    print(f"  • 總吞吐量: {thr.get('total', 0):.2f} req/s")
    
    # 添加 TTFT 指標（如果存在）
    ttft = report.get("ttft_ms", {})
    if ttft:
        print(f"  • 平均TTFT: {ttft.get('average', 0):.2f} ms")
        print(f"  • TTFT範圍: {ttft.get('min', 0):.2f} - {ttft.get('max', 0):.2f} ms")

    cpu = resu.get("cpu_percent", {})
    mem = resu.get("memory_percent", {})
    gpu = resu.get("gpu_percent", {})

    print("\n💻 資源使用情況:")
    print(f"  • CPU使用率: {cpu.get('average', 0):.1f}% (最高: {cpu.get('max', 0):.1f}%)")
    print(f"  • 記憶體使用率: {mem.get('average', 0):.1f}% (最高: {mem.get('max', 0):.1f}%)")
    print(f"  • GPU使用率: {gpu.get('average', 0):.1f}% (最高: {gpu.get('max', 0):.1f}%)")

    avg_tok = det.get("avg_tokens_per_response", {}).get("average", 0)
    print("\n🎯 輸出統計:")
    print(f"  • 平均回應tokens: {avg_tok:.2f}")
    print(f"  • 總請求數: {total_requests}")
    print(f"  • 成功請求數: {total_requests}")  # 假設都成功，實際可從報告中取得

    print("\n" + "=" * 80)