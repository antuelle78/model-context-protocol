
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WAZUH_URL=""
ENV WAZUH_SSL_VERIFY="true"
ENV WAZUH_TOKEN=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
