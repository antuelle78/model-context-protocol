
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure the ALPHAVANTAGE_API_KEY is set at runtime
ENV ALPHAVANTAGE_API_KEY=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
