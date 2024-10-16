docker rm -f unifi-protect-motion-detect-telegram-notification
docker run --restart=always --gpus all --network=host -d -v $(pwd)/data:/app/data --name unifi-protect-motion-detect-telegram-notification unifi-protect-motion-detect-telegram-notification:latest
