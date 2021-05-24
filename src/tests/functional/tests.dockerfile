FROM python:3.8-slim-buster

ENV DockerHOME=/home/app/tests/functional \
    PYTHONPATH=/home/app/ \
    PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1
RUN env

RUN mkdir -p $DockerHOME
WORKDIR $DockerHOME

RUN pip install --upgrade pip && apt-get update
COPY ./requirements.txt $DockerHOME/requirements.txt

RUN pip3 install -r ./requirements.txt

COPY ./ $DockerHOME/

ENTRYPOINT ["./test.entrypoint.sh"]

