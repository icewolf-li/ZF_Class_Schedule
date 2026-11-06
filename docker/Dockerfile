# syntax=docker/dockerfile:1
FROM python:3.13.9-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/browsers \
    UV_LINK_MODE=copy \
    UV_HTTP_TIMEOUT=180 \
    PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=180000 \
    UV_COMPILE_BYTECODE=0 \
    PATH=/app/.venv/bin:$PATH

WORKDIR /app
COPY docker/pyproject.toml docker/uv.lock ./
# uv 通过构建挂载使用，不进入最终镜像；仅下载 Chromium headless shell。
# 在同一层清理 apt 元数据，避免留在镜像的历史层中。
RUN --mount=from=ghcr.io/astral-sh/uv:0.12.0,source=/uv,target=/bin/uv \
    ["python", "-c", "import subprocess, shutil; subprocess.run(['uv', 'sync', '--frozen', '--no-dev', '--no-install-project'], check=True); subprocess.run(['/app/.venv/bin/python', '-m', 'playwright', 'install', '--with-deps', '--only-shell', 'chromium'], check=True); shutil.rmtree('/var/lib/apt/lists', ignore_errors=True); shutil.rmtree('/root/.cache', ignore_errors=True)"]

COPY docker/schedule_api.py docker/schedule_calendar.py cli/zf_schedule_monitor_uv.py ./
RUN ["python", "-c", "import os; os.makedirs('/app/data', exist_ok=True); os.chown('/app/data', 10001, 10001)"]
USER 10001:10001
EXPOSE 8000
CMD ["python", "schedule_api.py"]
