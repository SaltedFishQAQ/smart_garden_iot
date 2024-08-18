FROM python:3.11-slim

WORKDIR /app

COPY . /app

EXPOSE 8083

CMD ["bash", "-c", "PYTHONPATH=/app python service/user/__main__.py"]
