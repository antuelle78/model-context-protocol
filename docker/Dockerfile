# Builder stage
FROM python:3.13-slim as builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .
COPY data ./data
ENV PYTHONPATH="/app"

ARG SERVICENOW_USERNAME
ARG SERVICENOW_PASSWORD
ARG SERVICE_MANAGER_API_URL
ARG DATABASE_URL

ENV SERVICENOW_USERNAME=$SERVICENOW_USERNAME
ENV SERVICENOW_PASSWORD=$SERVICENOW_PASSWORD
ENV SERVICE_MANAGER_API_URL=$SERVICE_MANAGER_API_URL
ENV DATABASE_URL=$DATABASE_URL

ENV PATH="/opt/venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
