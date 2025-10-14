# Model Context Protocol (MCP) Server

This project implements a RESTful API that serves as the data backbone for Open‑webui, providing all the information required to generate high‑quality reports.

For detailed instructions on how to set up, run, and test the project, please refer to the [main README.md file](../README.md).

## Docker

The server runs inside a Docker container. Use the provided `docker-compose.yml` to spin it up:

```bash
docker-compose -f docker/docker-compose.yml up -d --build

