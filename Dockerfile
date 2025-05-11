FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

EXPOSE 8083

ENV PYTHONPATH="/app"

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "service/user/__main__.py"]
