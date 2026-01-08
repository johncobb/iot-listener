FROM python:3.9

ENV PYTHONUNBUFFERED 1

WORKDIR /code
RUN mkdir -p /code/log

COPY requirements.txt .
COPY vigil-watchdog/requirements.txt vigil-requirements.txt
RUN cat vigil-requirements.txt >> requirements.txt

RUN pip3 install -r requirements.txt

COPY src/ .
COPY vigil-watchdog/src/ services/vigil-watchdog

ENTRYPOINT ["supervisord", "-c", "/code/supervisord.conf"]
