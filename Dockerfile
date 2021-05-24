FROM python:3.8-slim-buster

ENV DockerHOME=/home/app/auth \
    PYTHONPATH=/home/app/ \
    PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1
RUN env

RUN mkdir -p $DockerHOME
WORKDIR $DockerHOME

EXPOSE 5000/tcp

RUN pip install --upgrade pip && apt-get update && apt-get install libpq-dev -y && apt-get install netcat -y
COPY ./src/requirements.txt $DockerHOME/requirements.txt

RUN pip3 install -r ./requirements.txt

COPY ./src $DockerHOME/

ENTRYPOINT ["./entrypoint.sh"]
