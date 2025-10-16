
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV EASYVISTA_URL=""
ENV EASYVISTA_API_KEY=""
ENV EASYVISTA_ACCOUNT_ID=""

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
