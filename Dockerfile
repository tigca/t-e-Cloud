FROM python:3.8
ADD . /
RUN apt update && apt upgrade -y && apt install -y git python3 python3-pip
RUN pip install pyTelegramBotAPI
RUN mkdir /data
CMD python app.py
