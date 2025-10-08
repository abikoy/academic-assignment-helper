FROM python:3.9-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Make pip more resilient on slow networks
ENV PIP_DEFAULT_TIMEOUT=180 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

# Upgrade pip first
RUN python -m pip install --upgrade pip setuptools wheel

# Copy requirements and install in stages (most stable packages first)
COPY requirements.txt .

# Install packages in groups to minimize failure impact
RUN pip install --retries 10 --timeout 180 \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-multipart==0.0.6

RUN pip install --retries 10 --timeout 180 \
    sqlalchemy==2.0.23 \
    psycopg2-binary==2.9.9 \
    pgvector==0.2.3

RUN pip install --retries 10 --timeout 180 \
    bcrypt==4.0.1 \
    passlib==1.7.4 \
    python-jose[cryptography]==3.3.0 \
    python-dotenv==1.0.0

RUN pip install --retries 10 --timeout 180 \
    pydantic==2.4.2 \
    email-validator==2.1.0.post1

RUN pip install --retries 10 --timeout 180 \
    openai==1.3.5 \
    httpx==0.24.1 \
    tiktoken==0.5.1 \
    requests==2.31.0

# Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
