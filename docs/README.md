# Model Context Protocol (MCP) Server

This project implements a RESTful API that serves as the data backbone for Open‑webui, providing all the information required to generate high‑quality reports.

For detailed instructions on how to set up, run, and test the project, please refer to the [main README.md file](../README.md).

## Features

- **News** CRUD (`POST /api/v1/40000/news`)
- **Suppliers** CRUD (`GET /suppliers`, `POST /suppliers`, `GET /suppliers/{id}/{comment}`)
- **Comments** CRUD (`POST /suppliers/{id}/comments`)
- **Generic table view** (`GET /{E_Your_Table}`)

All endpoints are documented in OpenAPI format and automatically served by FastAPI.

## Docker

The server runs inside a Docker container. Use the provided `docker-compose.yml` to spin it up:

```bash
docker-compose -f docker/docker-compose.yml up -d --build

