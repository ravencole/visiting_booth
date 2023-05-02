import signal
import sys
import argparse
import subprocess
from time import sleep
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import vlc as VLC

AUDIO_FILE = '/home/craven/test.mp3'
INPUT_PIN = 10
PLAYER = None

def getInput():
	return GPIO.input(INPUT_PIN)

def getIsOffHook():
	return getInput() == GPIO.LOW

def getIsOnHook():
	return getInput() == GPIO.HIGH

def init():
	print('Initializing...')

	print('Setting up VLC')

	global PLAYER

	# Setup VLC
	# ---------------------------
	# creating a vlc instance
	vlc = VLC.Instance('--input-repeat=999999')

	# creating a media
	media = vlc.media_new(AUDIO_FILE)

	# creating a media player
	PLAYER = vlc.media_player_new()

	# setting media to the player
	PLAYER.set_media(media)

	print('Setting up GPIO')

	# Setup GPIO
	# ---------------------------
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(INPUT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

	# Wait for phone to be hung up
	# ---------------------------
	while getIsOffHook():
		print('Waiting for phone to be put on the hook.')
		sleep(0.3)

	print('Initialization finished.')

def loop():
	print('Loop starting')

	playing = False

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
			subprocess.run('lp ./main.pdf', shell=True)

		sleep(0.2)

def cleanup():
	print('Cleaning up...')
	GPIO.cleanup()

def signal_handler(sig, frame):
	cleanup()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
	init()
	loop()
	cleanup()

main()