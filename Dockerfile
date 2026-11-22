FROM ubuntu:24.04

ENV PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/pandoc-mcp/bin:${PATH}"

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates pandoc python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv /opt/pandoc-mcp \
    && useradd --create-home pandoc-mcp

WORKDIR /app
COPY requirements.txt ./
# The server uses FastMCP from version 1 of the MCP SDK.
RUN pip install --no-cache-dir -r requirements.txt 'mcp<2'
COPY . .

USER pandoc-mcp
CMD ["python", "server.py"]
