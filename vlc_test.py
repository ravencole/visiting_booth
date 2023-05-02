import vlc
 
from time import sleep

media = vlc.MediaPlayer("/home/craven/Downloads/youre_in_maya.mp3")

media.play()

sleep(5)

media.pause()

print("Done...")

sleep(5)
