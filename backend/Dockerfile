# Multi-stage: build deps in one image, copy only the result into a clean one.
# Keeps the final image small and free of compilers.

FROM python:3.14-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.14-slim
# Run as a non-root user. Kubernetes can enforce this, and the default (root)
# is the single most common container security finding.
RUN useradd --create-home --uid 10001 app
COPY --from=builder /install /usr/local
WORKDIR /app
COPY main.py .
USER 10001
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
