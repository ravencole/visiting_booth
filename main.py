from glob import glob
import signal
import sys
import argparse
import subprocess
from time import sleep
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import vlc as VLC

AUDIO_FILE = '/home/craven/test.mp3'
PDF_DIRECTORY = '/home/craven/main/pdfs/*.pdf'
INPUT_PIN = 10
PLAYER = None
LOOP_SLEEP = 0.2

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
		sleep(LOOP_SLEEP)

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