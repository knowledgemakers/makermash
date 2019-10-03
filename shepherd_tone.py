import os
from music21 import stream, instrument
from music21.note import Note
from music21.midi.realtime import StreamPlayer
import pygame.midi
from time import sleep



class ShepherdMusic:
    volume_increment_u=0
    volume_increment_d=0
    def sheperd_tone(self, notes_i, length=0.5):

        intrument_to_play = instrument.Piano()
        # Highest octave, volume gets lower
        shepard_tone_u = stream.Part()
        shepard_tone_u.insert(0, intrument_to_play)
        c_major = ['C#5', 'D#5', 'E#5', 'F#5', 'G#5', 'A#5', 'B#5', 'C#6', 'D#6', 'E#6', 'F#6', 'G#6', 'A#6', 'B#6']
        c_major = [c_major[notes_i%len(c_major)]]

        for i in c_major:
            n = Note(i, quarterLength=length)
            n.volume.velocityScalar = 0.7 - self.volume_increment_u
            shepard_tone_u.append(n)
            self.volume_increment_u = self.volume_increment_u + 0.05

        # Middle octave, volume constant
        shepard_tone_m = stream.Part()
        shepard_tone_m.insert(0, intrument_to_play)
        c_major = ['C#3', 'D#3', 'E#3', 'F#3', 'G#3', 'A#3', 'B#3', 'C#4', 'D#4', 'E#4', 'F#4', 'G#4', 'A#4', 'B#4']
        c_major = [c_major[notes_i%len(c_major)]]

        for i in c_major:
            n = Note(i, quarterLength=length)
            shepard_tone_m.append(n)

        # Lowest octave, volume gets higher
        shepard_tone_l = stream.Part()
        shepard_tone_l.insert(0, intrument_to_play)
        c_major = ['C#1', 'D#1', 'E#1', 'F#1', 'G#1', 'A#1', 'B#1', 'C#2', 'D#2', 'E#2', 'F#2', 'G#2', 'A#2', 'B#2']
        c_major = [c_major[notes_i%len(c_major)]]

        for i in c_major:
            n = Note(i, quarterLength=length)
            n.volume.velocityScalar = 0.05 + self.volume_increment_d
            shepard_tone_l.append(n)
            self.volume_increment_d = self.volume_increment_d + 0.05

        return stream.Stream([shepard_tone_u, shepard_tone_m, shepard_tone_l])

    def play(self, i):
        player = StreamPlayer(self.sheperd_tone(i))
        player.play()

    def play_gameover(self):
        player = StreamPlayer(self.sheperd_tone(0, 1))
        player.play()




pygame.midi.init()
print("aaa")
for id in range(pygame.midi.get_count()):
  print (pygame.midi.get_device_info(id))

ShepherdMusic().play(0)

