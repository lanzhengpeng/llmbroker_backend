from fastapi import APIRouter
import os, time, psutil

router = APIRouter()
start_time = time.time()

@router.get("/monitor")
def monitor():
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / 1024 / 1024
    return {
        "status": "ok",
        "memory_mb": round(mem_mb, 2),
        "uptime_sec": round(time.time() - start_time)
    }

@router.get("/healthz")
def healthz():
    return "ok"