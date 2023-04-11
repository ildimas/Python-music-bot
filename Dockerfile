FROM python

WORKDIR /app_bot

COPY . .

RUN apt-get update && apt-get install -y ffmpeg
RUN pip install --no-cache-dir -r /app_bot/requirements.txt

CMD [ "python", "main_music_bot/main.py" ]