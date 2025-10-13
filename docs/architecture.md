# Project Architecture

This diagram illustrates the architecture of the project.

```
+------------------------+
| LM Studio / Open-webui |
+-----------+------------+
            |
            v
+-----------+------------+
|        Gateway         |
+-----------+------------+
            |
+-----------v------------+
|      Microservices     |
| (ServiceNow, GLPI)     |
+-----------+------------+
            |
+-----------v------------+
|       Mock APIs        |
| (ServiceNow, GLPI)     |
+-----------+------------+
            |
+-----------v------------+
|        Database        |
|        (SQLite)        |
+------------------------+
```