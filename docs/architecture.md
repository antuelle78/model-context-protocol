# Project Architecture

This diagram illustrates the architecture of the project.

```
+------------------------+
| LM Studio / Open-webui |
+-----------+------------+
            |
            v
+------------------------+
|       MCP Server       |
| (FastAPI Application)  |
+-----------+------------+
            |
            |----------------->+------------------------+
            |                  |      ServiceNow API      |
            |                  +------------------------+
            |
            |----------------->+------------------------+
            |                  |        GLPI API        |
            |                  +------------------------+
            |
            |----------------->+------------------------+
            |                  |      Yahoo Finance     |
            |                  +------------------------+
            |
            |----------------->+------------------------+
                               |     OpenWeather API    |
                               +------------------------+
```

The MCP Server is a single FastAPI application that provides a unified interface to a variety of tools. Some tools connect to external APIs (like ServiceNow, GLPI, Yahoo Finance, and OpenWeather), while others provide access to local resources (like the file system).