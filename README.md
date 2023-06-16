### Introduce
This python script is using UniFi API to  get `latest` `specific` camera detection video from UniFi Protect and send it to telegram. The script is not perfect. It's just a `it works` tool which is very simple.

![Telegram copy](https://github.com/m2nx/unifi-protect-motion-detect-telegram-notification/assets/16236902/0bdf8a54-8a3b-419d-8c0f-8171f8b5e0bb)

### Required steps
1. you need to register a telegram bot to get `BOT_TOKEN` first.

2. then you should login to your UniFi Protect to get your `CAMERA_ID`.  

* open page https://`your_unifi_host`/protect/events
* on display option, choose the camera you want to check
* right click your mouse on the page, click Inspect to open developer tools. select the `Network` tab
* click one of these detections. then you should see a new requests like `events?cameras=614f6XXXXX`
* click this request and you will see the detail page. focus on the `Request URL`, copy the camera id like `614fxxxxxxxxxxxxxxxxxxxx `
4. last one is `TELEGRAM_CHAT_ID`. you can search on google to learn how to get it.

Now put all parameters in `config.ini` file. set it correctly before run this script.


### How to use
```
git clone https://github.com/m2nx/unifi-protect-motion-detect-telegram-notification.git

cd unifi-protect-motion-detect-telegram-notification

docker build -t unifi-protect-motion-detect-telegram-notification .

docker run -d -v $(pwd)/data:/app/data --name unifi-protect-motion-detect-telegram-notification unifi-protect-motion-detect-telegram-notification
```

### Debug
this script use `shelve` built-in package. when you run -v in `docker `command. it will map the file `data/shelve.db` to your docker host.  if you get in trouble with this script. you can delete this file and restart again. 

use `docker logs -f unifi-protect-motion-detect-telegram-notification -f --tail 500` to check the log

![image](https://github.com/m2nx/unifi-protect-motion-detect-telegram-notification/assets/16236902/76ed8eab-eaa9-41bc-b34a-82e9502d5c59)

### API
`https://${UNIFI_HOST_IP}/proxy/protect/api/events?allCameras=true&end&limit=100&orderDirection=DESC&start&types=motion&types=ring&types=smartDetectZone&types=smartDetectLine`

`https://${UNIFI_HOST_IP}/proxy/protect/api/video/export?camera=614xxxxxxxxxxxxxxxed&channel=0&end=1680145112345&filename=UVC%20G3%20XXXX%20-%203-30-2023,%2010.59.36.mp4&start=1680145112345`
```json
[
    {
    "id": "6425b58f00xxxxxxxxxxxxxx",
    "type": "motion",
    "start": 1680192xxxxxx,
    "end": 16801929xxxxx,
    "score": 100,
    "smartDetectTypes": [],
    "smartDetectEvents": [],
    "camera": "614f6xxxxxxxxxxxxxxxxxxx",
    "partition": null,
    "user": null,
    "metadata": {},
    "thumbnail": "e-xxxxxxxxxxxxxxxxxxxx",
    "heatmap": "e-xxxxxxxxxxxxxxxxxxx",
    "modelKey": "event",
    "timestamp": 1680191234567
    }
]
```
