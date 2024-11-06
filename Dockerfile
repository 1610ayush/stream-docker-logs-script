# Dockerfile for Python Log Forwarder
FROM python:3.8-slim

WORKDIR /app
COPY log_forwarder.py /app/

RUN pip install requests

CMD ["python", "log_forwarder.py"]
