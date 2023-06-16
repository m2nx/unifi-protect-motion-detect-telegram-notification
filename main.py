import requests
import json
import time
import telebot
import logging
import configparser
import shelve

# set config
logging.basicConfig(encoding='utf-8', level=logging.INFO)
requests.packages.urllib3.disable_warnings()
config = configparser.ConfigParser()
config.read('config.ini')

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

# start unifi session
session = requests.Session()
session.post(host + '/api/auth/login', data={'username': username, 'password': password, 'remember': True}, verify=False)

# start telegram bot
telegram_bot = telebot.TeleBot(bot_token, parse_mode=None)
telegram_bot.send_message(telegram_chat_id, 'bot start running....')

while True:
    # 1. get latest videos json
    list_motion_videos = session.get(f"{host}/proxy/protect/api/events", params={ 'allCameras': True, 'limit': 5, 'orderDirection': 'DESC', 'types': 'motion'})
    logging.debug('checking latest motion detection info.')

    # get video info success
    if list_motion_videos.status_code != 200:
        logging.info('get unifi events error.')
        continue

    logging.debug('get latest video info success.')
    videos = json.loads(list_motion_videos.content)

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
            telegram_bot.send_video(telegram_chat_id, file_motion.content)
            logging.info(f"video {video['id']} sent.")
            db['data'][video['id']] = True
            # write back from mem to db
            db.sync()
        except Exception:
            logging.info('send video failed. please check your network.')
    db.close()
    time.sleep(interval_time)
