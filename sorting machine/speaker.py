import pygame
import time
import csv

class Speaker:

    def singSong(self,signature):   # Method playing the audio for the detected signature.
        track = self.identifyTrack(signature)
        self.sing(track)

    def sing(self,track): 
        pygame.mixer.init()
        pygame.mixer.music.load("audio/" + track)
        pygame.mixer.music.play()
        time.sleep(4)

    def identifyTrack(self, signature): # Reading the name of the audio file for the given sigature from the 'signature.csv' file
        with open('signatures.csv') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',' )
            for row in readCSV:
                if row[0] == str(signature):
                    return row[2]