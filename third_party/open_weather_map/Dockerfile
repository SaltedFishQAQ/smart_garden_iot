FROM python:3.9-slim

WORKDIR /app

COPY weather_service.py /app/
COPY weather_api_adapter.py /app/
COPY config_loader.py /app/
COPY weather_config.xml /app/
COPY requirements.txt /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "weather_api_adapter.py"]
