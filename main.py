import requests
import json
import time
import telebot
import logging
import configparser
import shelve
import io
import tempfile
from moviepy.editor import *

# set config
logging.basicConfig(encoding='utf-8', level=logging.DEBUG)
requests.packages.urllib3.disable_warnings()
config = configparser.ConfigParser()
config.read('config.ini')
print('start config')
# get params from config parser
interval_time = int(config['DEFAULT'].get('INTERVAL_TIME', 5))
is_ssl = config['DEFAULT'].getboolean('USE_SSL', True)
host = config['DEFAULT'].get('HOST', 'localhost')
bot_token = config['DEFAULT'].get('BOT_TOKEN')
telegram_chat_id = config['DEFAULT'].get('TELEGRAM_CHAT_ID')
camera_id = config['DEFAULT'].get('CAMERA_ID')
scheme = 'https://' if is_ssl else 'http://'
host = scheme + host
username = config['DEFAULT'].get('USERNAME')
password = config['DEFAULT'].get('PASSWORD')
print(config['DEFAULT'])

# start unifi session
print('start session')
session = requests.Session()
res = session.post(host + '/api/auth/login', data={'username': username, 'password': password, 'remember': True}, verify=False)
print(res)

# start telegram bot
telegram_bot = telebot.TeleBot(bot_token, parse_mode=None)
telegram_bot.send_message(telegram_chat_id, 'bot start running....')

print(1)
while True:
    # 1. get latest videos json
    #list_motion_videos = session.get(f"{host}/proxy/protect/api/events", params={ 'allCameras': True, 'limit': 5, 'orderDirection': 'DESC', 'types': 'motion', 'types': 'smartDetectZone', 'types': 'smartDetectLine', 'types': 'smartAudioDetect', 'types': 'ring', 'types': 'doorAccess'})
    # motion detection  https://10.10.10.5/proxy/protect/api/detection-search?labels=camera%3A614f625b02de2e03e70003ed&limit=100&orderDirection=DESC
    list_motion_videos = session.get(f"{host}/proxy/protect/api/detection-search", params={ 'limit': 5, 'orderDirection': 'DESC', 'labels': f'camera:{camera_id}'})
    logging.debug('checking latest motion detection info.')
    print(2)

    # get video info success
    if list_motion_videos.status_code != 200:
        print(3)
        logging.info(list_motion_videos.status_code)
        logging.info(list_motion_videos.content)
        logging.info('get unifi events error.')
        session.post(host + '/api/auth/login', data={'username': username, 'password': password, 'remember': True}, verify=False)
        continue

    print(4)
    logging.debug('get latest video info success.')
    videos = json.loads(list_motion_videos.content)['events']
    print(5)

    db = shelve.open('data/shelve', writeback=True)
    # dictionary in shelve data
    if 'data' not in db:
        logging.info('shelve db initing.')
        db['data'] = {}

    # if video id not in data, then create new one with value False.
    for video in videos:
        if db['data'].get(video['id']):
            continue

        # found video, set False in db
        logging.info(f"found video {video['id']}, start download video...")
        db['data'][video['id']] = False
        file_motion = session.get(f'{host}/proxy/protect/api/video/export', params={'camera': camera_id, 'channel': 0, 'start': video['start'], 'end': video['end']})
        if file_motion.status_code != 200:
            logging.info('download video error.')
            continue
        try:
            logging.info('download success. start sending to telegram.')
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=True) as temp_video_file:
                temp_video_file.write(file_motion.content)
                temp_video_file.flush()  # Ensure all data is written

                # Load the video from the temporary file
                clip = VideoFileClip(temp_video_file.name).rotate(270)

                # Save the rotated clip to a new temporary file before sending
                output_filename = 'rotated_video.mp4'
                clip.write_videofile(output_filename, codec='libx264')

                # Save the rotated clip as a GIF

                # Send the video to Telegram
                with open(output_filename, 'rb') as file:
                    telegram_bot.send_video(telegram_chat_id, file)
                    #telegram_bot.send_document(telegram_chat_id, file)

            logging.info('Video sent to Telegram.')
            #print(type(file_motion.content))
            #video_bytes_io = io.BytesIO(file_motion.content)
            #print(type(video_bytes_io))
            #clip = VideoFileClip(video_bytes_io).rotate(90)
            #print(f'@@@@@@@@@@@@{type(clip)}')

            #telegram_bot.send_video(telegram_chat_id, clip)
            #telegram_bot.send_video(telegram_chat_id, file_motion.content)
            logging.info(f"video {video['id']} sent.")
            db['data'][video['id']] = True
            # write back from mem to db
            db.sync()
        except Exception as e:
            logging.info(f'send video failed. please check your network.{e}')
    db.close()
    time.sleep(interval_time)
