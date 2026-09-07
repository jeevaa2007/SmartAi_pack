# ==========================================
# STAGE 1: Dependency Compiler (Builder)
# ==========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/

# Install python dependencies to a local folder directory
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# STAGE 2: Lightweight Security Runtime
# ==========================================
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Install runtime dependencies for PostgreSQL client and OpenCV headless rendering libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-privileged system user for container execution
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -m -s /sbin/nologin appuser

# Copy installed modules from builder stage
COPY --from=builder /root/.local /home/appuser/.local
COPY . /app

# Transfer ownership of application files to non-root user
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
