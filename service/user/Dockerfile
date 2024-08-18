FROM python:3.11-slim

WORKDIR .

COPY ../../ .

EXPOSE 8083

ENV PYTHONPATH=""

CMD ["python", "service/user/__main__.py"]
