import signal
import subprocess
import sys

import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
import vlc as VLC

from glob import glob
from time import sleep

AUDIO_DIRECTORY = '/home/craven/main/audio/*'
PDF_DIRECTORY = '/home/craven/main/pdfs/*.pdf'
INPUT_PIN = 10
LOOP_SLEEP = 0.2
PLAYER = None

def getInput():
    return GPIO.input(INPUT_PIN)


def getIsOffHook():
    return getInput() == GPIO.LOW


def getIsOnHook():
    return getInput() == GPIO.HIGH


def initVLC():
    print('init VLC')

    global PLAYER

    # creating a vlc instance
    vlc = VLC.Instance()

    tracks = glob(AUDIO_DIRECTORY)

    medialist = vlc.media_list_new()

    for t in tracks:
        medialist.add_media(vlc.media_new(t))

    PLAYER = vlc.media_list_player_new()

    PLAYER.set_playback_mode(VLC.PlaybackMode.loop)

    PLAYER.set_media_list(medialist)


def initGPIO():
    print('init GPIO')

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def initPhoneState():
    print('init phone state')

    while getIsOffHook():
        print('Waiting for phone to be put on the hook.')
        sleep(LOOP_SLEEP)


def init():
    print('Initializing...')

    initVLC()

    initGPIO()

    initPhoneState()

    print('Initialization finished.')


def loop():
    print('Loop starting')

    playing = False

    pdfs = glob(PDF_DIRECTORY)

    i = 0;

    while True:
        if getIsOffHook() and playing == False:
            print('Playing')
            playing = True
            PLAYER.play()
        elif getIsOnHook() and playing == True:
            print('Pausing')
            playing = False
            PLAYER.pause()
            print('Printing')
            pdf_file = pdfs[i]
            subprocess.run(f'lp {pdf_file}', shell=True)
            i += 1
            if i > 3:
                i = 0

        sleep(LOOP_SLEEP)


def cleanup():
    print('Cleaning up...')
    GPIO.cleanup()


def signal_handler(sig, frame):
    cleanup()
    sys.exit(0)


def main():
    # Set SIGINT intercept
    signal.signal(signal.SIGINT, signal_handler)

    # Setup
    init()

    # Run
    loop()

    # Bye
    cleanup()


# Start
main()
