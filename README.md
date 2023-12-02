# EAMWatch-Bot

## Setup
```sh
git clone https://github.com/sniper7kills/EAMWatch-Bot.git
cd EAMWatch-Bot
pip install -r requirements.txt
```

## Running:
1) Obtain API Token
2) Obtain Webhook URL
3) Update `VARIABLES.py` with information obtained
4) Open SDR; Tune Radio; Enable Squelch
5) Run the recording script `./record.sh`
6) Run the transcription script `./run.py`

### Prep after shutdown
```
rm -rf ./recordings/*.wav
rm -rf ./audio.wav
```
