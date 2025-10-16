
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the Grafana URL and API token are set at runtime
ENV GRAFANA_URL=""
ENV GRAFANA_API_TOKEN=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
