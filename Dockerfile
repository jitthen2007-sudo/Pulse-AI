# Production Multi-Stage Dockerfile for Pulse AI
FROM python:3.11-slim AS backend-stage

WORKDIR /app
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY api/ ./api/

# Node.js Stage
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Final Runner
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y nodejs npm curl && rm -rf /var/lib/apt/lists/*

COPY --from=backend-stage /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-stage /usr/local/bin /usr/local/bin
COPY --from=frontend-builder /app ./

EXPOSE 3000
EXPOSE 8000

ENV PORT=8000
ENV HOST=0.0.0.0

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port 8000 & npm run start"]
