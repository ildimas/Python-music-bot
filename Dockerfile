FROM python
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app_bot

COPY . .

RUN apt-get update && \
    apt-get install -y python3-pip ffmpeg && \
    pip3 install --no-cache-dir -r /app_bot/requirements.txt

CMD [ "python3", "/app_bot/main_music_bot/main.py" ]