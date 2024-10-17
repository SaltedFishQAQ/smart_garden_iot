FROM python:3.9-slim

WORKDIR /usr/src/app

COPY ./bot.py /usr/src/app/
COPY ./authenticator.py /usr/src/app/
COPY ./notification.py /usr/src/app/
COPY ./mqtt.py /usr/src/app/
COPY ./plant.py /usr/src/app/
COPY ./config.xml /usr/src/app/
COPY ./requirements.txt /usr/src/app/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "bot.py"]

