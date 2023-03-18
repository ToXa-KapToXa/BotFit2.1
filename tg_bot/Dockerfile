FROM python:3.8

WORKDIR /opt/app

COPY tg_bot/requirements.txt .

RUN pip3 install -r /opt/app/requirements.txt

COPY ./tg_bot .

RUN mkdir db

CMD python3 main.py