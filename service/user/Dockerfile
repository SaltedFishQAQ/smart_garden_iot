FROM python:3.11-slim

WORKDIR /app

COPY ../ /app

EXPOSE 8083

ENV PYTHONPATH="/"

CMD ["python", "service/user/__main__.py"]
