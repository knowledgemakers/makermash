#!/usr/bin/env python
# coding: utf8
from __future__ import absolute_import, division, print_function
from itertools import cycle
import pygame
import random
import time
import RPi.GPIO as GPIO
from time import sleep



VISITOR_TTF_FILENAME = 'fonts/monopixies.ttf'
BLINK_EVENT = pygame.USEREVENT + 0
UPDATE_NUMBER = pygame.USEREVENT+1
REST_TIME = pygame.USEREVENT+2


flash = [26,20,8,15,6,16,27,9,11]

leds = [26,20,8,15,6,16,27,9,11]

mem_leds = [26,20,15,6,27,9,11] # currrent working LEDS :(

buttons = [17,22,12,5,10,13,14,18,21]

NUM_TO_LEDS = {
    "1": 26,
    "2": 20,
    "3": 8,
    "4": 16,
    "5": 6,
    "6": 15,
    "7": 27,
    "8": 9,
    "9": 11
}

global current_file, version

def gpio_setup():
    global pressed
    GPIO.setmode(GPIO.BCM)
    for each in buttons:
        GPIO.setup(each, GPIO.IN, GPIO.PUD_DOWN)

    for each in leds:
        GPIO.setup(each, GPIO.OUT)
    pressed = False


class MakerMasher():
    BLINK_EVENT = pygame.USEREVENT + 0
    screen=None
    screen_rect=None
    font = None
    current_score=3
    events = []
    target_results=[]
    target_results_iter=None
    in_game=False
    correct=0

    def __init__(self, font, screen):
        self.font = font
        self.screen=screen
        self.screen_rect=screen.get_rect()
        self.off_text_surface = pygame.Surface(self.screen_rect.size)

    def write_text_on_screen(self, text):
        self.screen.blit(self.off_text_surface, self.screen_rect)
        text_lines = text.split("\n")
        lines=0
        for line in text_lines:
            on_text_surface = self.font.render(
                line, True, pygame.Color('green3')
            )
            blink_rect = on_text_surface.get_rect()
            blink_rect.center = self.screen_rect.center
            blink_rect.centery = blink_rect.centery+50*lines
            self.screen.blit(on_text_surface, blink_rect)
            lines += 1

    def start_game(self):
        pygame.time.set_timer(REST_TIME, 0)
        self.correct=0
        self.in_game = False
        self.target_results = self.generate_result_based_on_score(self.current_score)
        self.target_results_iter = iter(self.target_results)
        self.flash_button(next(self.target_results_iter))
        now=time.time()
        self.in_game=False
        pygame.time.set_timer(UPDATE_NUMBER, 1000)

    def flash_button(self, val):
        gpio_value= NUM_TO_LEDS[val]
        print("flash button" + str(gpio_value))
        for each in range(0, 2):
            GPIO.output(gpio_value, True)
            sleep(0.1)
            GPIO.output(gpio_value, False)
            sleep(0.1)
        return

    def keep_printing(self):
        print("keep printing")
        next_number = next(self.target_results_iter, None)
        print ("next" + str(next_number))
        if next_number:
            self.flash_button(next_number)
        else:
            self.write_text_on_screen("GO!")
            self.in_game = True
            self.target_results_iter = iter(self.target_results)
            print(self.target_results)
            pygame.time.set_timer(UPDATE_NUMBER, 0)

    def generate_result_based_on_score(self, score):
        target= []
        for i in range(score+1):
            target.append(str(random.randint(0,8)))
        return target

    def process_key_down(self, key):
        if key == pygame.K_SPACE:
            self.start_game()
        if pygame.K_0 <= key <= pygame.K_9:
            print(key)
            if self.in_game:
                print("no")
                self.check_response(pygame.key.name(key))
        else:
            print(key)
        return

    def check_response(self, key):

        next_number = next(self.target_results_iter, None)
        print("is key {} the same as {}".format(key, next_number))
        if next_number:
            if next_number==key:
                self.correct += 1
                if self.correct == len(self.target_results):
                    self.win_and_next()
            else:
                self.game_over()

    def win_and_next(self):
        self.current_score+=1
        print(self.current_score)
        self.write_text_on_screen("WELL DONE!")
        pygame.time.set_timer(REST_TIME, 1000)

    def reset(self):
        self.in_game = False
        self.correct = 0
        self.current_score=3

    def game_over(self):
        self.write_text_on_screen("GAME OVER!\nYOUR SCORE: {}".format(self.current_score))
        self.reset()

    def process_gpio_buttons(self):
        global pressed
        if GPIO.input(21) and GPIO.input(22) and not pressed:
            pressed = True
            GPIO.output(26, True)
            GPIO.output(11, True)
            sleep(2)

        if GPIO.input(22) and not pressed:
            print('Button 1')

            pressed = True
            self.process_key_down(pygame.K_1)
            for each in range(0, 5):
                GPIO.output(26, True)
                sleep(0.1)
                GPIO.output(26, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(13) and not pressed:
            print('Button 2')
            pressed = True
            self.process_key_down(pygame.K_2)
            for each in range(0, 5):
                GPIO.output(20, True)
                sleep(0.1)
                GPIO.output(20, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(18) and not pressed:
            print('Button 3')
            pressed = True
            self.process_key_down(pygame.K_3)
            for each in range(0, 5):
                GPIO.output(8, True)
                sleep(0.1)
                GPIO.output(8, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(12) and not pressed:
            print('Button 4')
            pressed = True
            self.process_key_down(pygame.K_4)
            for each in range(0, 5):
                GPIO.output(16, True)
                sleep(0.1)
                GPIO.output(16, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(5) and not pressed:
            print('Button 5')
            pressed = True
            self.process_key_down(pygame.K_5)
            for each in range(0, 5):
                GPIO.output(6, True)
                sleep(0.1)
                GPIO.output(6, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(14) and not pressed:
            print('Button 6')
            pressed = True
            self.process_key_down(pygame.K_6)
            for each in range(0, 5):
                GPIO.output(15, True)
                sleep(0.1)
                GPIO.output(15, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(17) and not pressed:
            print('Button 7')
            pressed = True
            self.process_key_down(pygame.K_7)
            for each in range(0, 5):
                GPIO.output(27, True)
                sleep(0.1)
                GPIO.output(27, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(10) and not pressed:
            print('Button 8')
            pressed = True
            self.process_key_down(pygame.K_8)
            for each in range(0, 5):
                GPIO.output(9, True)
                sleep(0.1)
                GPIO.output(9, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False

        if GPIO.input(21) and not pressed:
            print('Button 9')
            pressed = True
            self.git(pygame.K_9)
            for each in range(0, 5):
                GPIO.output(11, True)
                sleep(0.1)
                GPIO.output(11, False)
                sleep(0.1)
            sleep(0.5)
            pressed = False


def main():
    gpio_setup()
    pygame.init()
    try:

        clock = pygame.time.Clock()
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(VISITOR_TTF_FILENAME, 50)
        masher = MakerMasher(font, screen)

        masher.write_text_on_screen("Press Any key")

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.KEYDOWN:
                    masher.process_key_down(event.key)
                if event.type == UPDATE_NUMBER:
                    masher.keep_printing()
                if event.type == REST_TIME:
                    masher.start_game()
            masher.process_gpio_buttons()

            pygame.display.update()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()