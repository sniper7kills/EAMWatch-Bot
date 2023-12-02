#!/usr/bin/python3

import os
import time
import datetime
from discordwebhook import Discord
import soundfile as sf
import re
from VARIABLES import WEBHOOK_URL, SITE_TOKEN
import requests


# Get the list of all files and directories
path = "./recordings"


def getFileList():
    global path
    dir_list = os.listdir(path)
    return sorted(dir_list)[0:-1]


def getFileSizeKB(fileName):
    global path
    fullFilePath = path + "/" + fileName
    return os.path.getsize(fullFilePath) / 1024

def getAudioLength(fileName):
    global path
    f = sf.SoundFile(path + "/" + fileName)
    return f.frames / f.samplerate

def processAudioFile(fileName):
    global path
    os.system("ffmpeg -i " + path + "/" + fileName + " -ar 16000 -ac 1 -c:a pcm_s16le ~/Desktop/automation/audio.wav;")
    #os.system("cp " + path + "/" + fileName + " ~/Desktop/automation/audio.wav")
    os.system("~/Desktop/whisper.cpp/main -pc -m ~/Desktop/whisper.cpp/models/ggml-large.bin -f ~/Desktop/automation/audio.wav -otxt")

def getAudioTranscript():
    fileContent = ''
    with open("audio.wav.txt", 'rb') as file:
    	lines = file.readlines()
    	
    	for line in lines:
            line = line.decode('utf-8', errors='ignore')
            fileContent =fileContent + line
    	
    return fileContent

def cleanTranscript(transcript):

    transcript = re.sub("\[[\s\S]*\]", "",transcript)
    transcript = re.sub("\([\s\S]*\)", "",transcript)
    transcript = re.sub("\*[\s\S]*\*", "",transcript)

    transcript = transcript.replace("\n", "")
    transcript = transcript.replace("\r", "")

    while "  " in transcript:
        transcript = transcript.replace("  ", " ")

    return transcript


def getAudioEndTimeUTC(fileName):
    global path
    timestamp = os.path.getmtime(path + "/" + fileName)
    print(timestamp)
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat()

def getAudioStartTimeUTC(fileName):
    global path
    timestamp = os.path.getmtime(path + "/" + fileName) - getAudioLength(fileName)
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat()


def postMessage(fileName, fileContent):
    global WEBHOOK_URL, path
    url = WEBHOOK_URL
    discord = Discord(url=url)

    if len(fileContent) > 2000:
        fileContent = "CONTENT TOO LONG FOR DISCORD!\n" + getAudioStartTimeUTC(fileName)

    discord.post(
        file={
            fileName: open("audio.wav", "rb"),
        },
        content=fileContent,
    )

def getUploadData():
    global SITE_TOKEN

    uploadData = requests.post(
        'https://eam.watch/api/vapor/signed-storage-url',
        headers={"Authorization": "Bearer " + SITE_TOKEN},
    )
    uploadData = uploadData.json()
    if "url" in uploadData:
        return uploadData
    else:
        print("Site Issue... Retrying...")
        time.sleep(5)
        return getUploadData()

def uploadRecording(fileName):
    global path, SITE_TOKEN

    uploadData = getUploadData()

    uploadResponse = requests.put(uploadData['url'], data=open("audio.wav", "rb").read())
    
    data = {
        'time': getAudioStartTimeUTC(fileName),
        'frequency': 11175,
        'receiver': None,
        'uuid': uploadData['uuid'],
        'bucket': uploadData['bucket'],
        'key': uploadData['key'],
        'name': 'automated.wav',
        'content_type': 'application/octet-stream'
    }
    r = requests.post(
        "https://eam.watch/api/automatedRecordings",
        data=data,
        headers={"Authorization": "Bearer " + SITE_TOKEN},
    )


##################################################################################################################################################################

def attemptWebsiteFormat(message):
    commands = {
        "stand by": "\n",
        "standby": "\n",
        "break": "\n",
        "all stations": "ALLSTATIONS",
        "i say again": "\n",
        "this is": "\nTHIS_IS:",
        "message follows": "\n",
    }

    phonetic = {
        "alpha": "a",
        "bravo": "b",
        "charlie": "c",
        "delta": "d",
        "echo": "e",
        "foxtrot": "f",
        "golf": "g",
        "gulf": "g",
        "hotel": "h",
        "india": "i",
        "juliet": "j",
        "kilo": "k",
        "lima": "l",
        "mike": "m",
        "november": "n",
        "oscar": "o",
        "papa": "p",
        "quebec": "q",
        "romeo": "r",
        "sierra": "s",
        "tango": "t",
        "uniform": "u",
        "unicorn": "u",
        "victor": "v",
        "whiskey": "w",
        "x-ray": "x",
        "yankee": "y",
        "zulu": "z",
        "1": "1",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "6": "6",
        "7": "7",
        "8": "8",
        "9": "9",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "zero": "0",
        "\n": "\n"
    }

    message = message.replace(",", "")
    message = message.replace(".", "")
    message = message.replace("!", "")
    message = message.lower()

    for command in commands:
        message = message.replace(command, commands[command])

    words = message.split(" ")

    output = ""


    for word in words:
        if word.lower() in phonetic:
            output = output + phonetic[word.lower()]
        else:
            output = output + "(" + word + ")"

    return output


##################################################################################################################################################################



while True:
    for fileName in getFileList():
        if getFileSizeKB(fileName) > 1000 and getAudioLength(fileName) > 10:
            processAudioFile(fileName)
            transcript = cleanTranscript(getAudioTranscript())
            if len(transcript) > 10:
                uploadRecording(fileName)
                postMessage(fileName,
                    "Broadcasted At: " + getAudioStartTimeUTC(fileName) + "\n" +
                    "Transcription Attempt: `" + attemptWebsiteFormat(transcript) + "`\n" +
                    transcript
                )
            os.system("rm ~/Desktop/automation/audio.wav ~/Desktop/automation/audio.wav.txt")
        os.system("rm " + path + "/" + fileName )

