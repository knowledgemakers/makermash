#!/usr/bin/env python
# coding: utf8
from __future__ import absolute_import, division, print_function
from itertools import cycle
import pygame
import random
import time
import RPi.GPIO as GPIO
from time import sleep
from shepherd_tone import ShepherdMusic
from leaderboard import Leaderboard
import pygame.midi



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

KEY_TO_GPIO = {
    pygame.K_1: 26,
    pygame.K_2: 20,
    pygame.K_3: 8,
    pygame.K_4: 16,
    pygame.K_5: 6,
    pygame.K_6: 15,
    pygame.K_7: 27,
    pygame.K_8: 9,
    pygame.K_9: 11
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
    finish_print=False
    read_input = False
    player_name=""
    logos={}
    image_rect={}

    def __init__(self, font, screen):

        self.font = font
        self.screen=screen


        self.screen_rect=screen.get_rect()
        self.off_rect = self.screen_rect.copy()
        self.off_rect.height=self.screen_rect.height - 200
        self.off_text_surface = pygame.Surface(self.off_rect.size)
        print(self.off_rect)
        logos = pygame.image.load("img/kmakers.png")
        image_rect = logos.get_rect()
        image_rect.y = self.screen_rect.height-70
        image_rect.x = self.screen_rect.width - 210
        self.screen.blit(logos, image_rect)
        self.music = ShepherdMusic()
        self.leaderboard = Leaderboard()
        self.reset_buttons()
    def set_logo(self):
        if not self.logos:
            self.logos = pygame.image.load("img/kmakers.png")
            self.image_rect = self.logos.get_rect()
            self.image_rect.y = self.screen_rect.height - 70
            self.image_rect.x = self.screen_rect.width - 210
        self.screen.blit(self.logos, self.image_rect)

    def write_text_on_screen(self, text):
        print(self.off_rect)
        print(self.off_text_surface)
        self.screen.fill((0, 0, 0))
        self.set_logo()
        text_lines = text.split("\n")
        lines = 0
        for line in text_lines:
            on_text_surface = self.font.render(
                line, True, pygame.Color('green3')
            )
            blink_rect = on_text_surface.get_rect()
            blink_rect.center = self.screen_rect.center
            if len(text_lines) > 6:
                blink_rect.centery = blink_rect.centery + 50 * lines - (50 * (len(text_lines) - 6))
            else:
                blink_rect.centery = blink_rect.centery + 50 * lines
            self.screen.blit(on_text_surface, blink_rect)
            lines += 1

    def start_game(self):
        pygame.time.set_timer(REST_TIME, 0)
        self.reset_buttons()
        self.screen.fill((0, 0, 0))
        self.write_text_on_screen("GET READY...")
        self.correct=0
        self.in_game = False
        pygame.display.flip()
        self.target_results = self.generate_result_based_on_score(self.current_score)
        self.target_results_iter = iter(self.target_results)
        self.flash_button(next(self.target_results_iter))
        self.finish_print=False
        pygame.time.set_timer(UPDATE_NUMBER, 100)

    def button_on(self, val):
        gpio_value = NUM_TO_LEDS[val]
        GPIO.output(gpio_value, True)
        return

    def button_off(self, val):
        gpio_value = NUM_TO_LEDS[val]
        GPIO.output(gpio_value, False)
        return

    def gameover_show(self):
        sleep(0.5)
        self.button_on("2")
        self.button_on("4")
        self.button_on("5")
        self.button_on("6")
        self.button_on("8")

    def reset_buttons(self):
        self.button_off("1")
        self.button_off("2")
        self.button_off("3")
        self.button_off("4")
        self.button_off("5")
        self.button_off("6")
        self.button_off("7")
        self.button_off("8")
        self.button_off("9")


    def flash_button(self, val):
        print("flashing" + val)
        gpio_value= NUM_TO_LEDS[val]
        self.music.play(int(val))

        print("flash button" + str(gpio_value))
        for each in range(0, 2):
            GPIO.output(gpio_value, True)
            sleep(0.1)
            GPIO.output(gpio_value, False)
            sleep(0.1)
        return

    def keep_printing(self):
        if self.finish_print:
            return
        print("keep printing")
        next_number = next(self.target_results_iter, None)
        print ("next " + str(next_number))
        if next_number:
            self.flash_button(next_number)
        else:
            pygame.time.set_timer(UPDATE_NUMBER, 0)
            self.write_text_on_screen("GO!")
            self.in_game = True
            self.target_results_iter = iter(self.target_results)
            print("target result" + str(self.target_results))
            self.finish_print=True
            self.music = ShepherdMusic()

    def generate_result_based_on_score(self, score):

        target= []
        prev_num=0
        for i in range(score+1):
            number = random.randint(1,9)
            while number == 3 or number==prev_num or (score<=4 and number==5):
                number = random.randint(1, 9)
            target.append(str(number))
            prev_num=number
        print(target)
        return target

    def process_key_down(self, key):
        if key == pygame.K_SPACE:
            self.start_game()
        if pygame.K_0 <= key <= pygame.K_9:
            print(key)
            if self.in_game:
                print("no")
                self.check_response(pygame.key.name(key))
        elif pygame.K_a <= key <= pygame.K_z:
            if self.read_input:
                self.process_input_letter(pygame.key.name(key))
        elif key == pygame.K_RETURN or key  == pygame.K_KP_ENTER:
            self.finish_player_name()
        else:
            print(key)
        return

    def process_input_letter(self, letter):
        if len(self.player_name)==3:
            self.finish_player_name()
            return
        self.player_name += letter.upper()
        self.write_text_on_screen(self.player_name + "_")


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
        else:
            self.game_over()

    def win_and_next(self):
        self.current_score+=1
        self.write_text_on_screen("WELL DONE! \n GET READY...")
        pygame.time.wait(1000)
        pygame.time.set_timer(REST_TIME, 2000)

    def reset(self):
        self.in_game = False
        self.correct = 0
        self.current_score=3

    def game_over(self):
        if self.leaderboard.is_highscore(self.current_score):
            self.get_player_name()
        else:
            self.write_text_on_screen("GAME OVER!\nYOUR SCORE: {} \n  PRESS CENTRAL BUTTON TO START".format(self.current_score) + "\n" + self.leaderboard.get_highscore_string())
            self.leaderboard.write("na", self.current_score)
            self.reset()
        self.music.play_gameover()
        self.gameover_show()




    def get_player_name(self):
        self.write_text_on_screen("YOU MADE IT TO THE TOP 5! \n ENTER YOUR INITIALS!")
        self.read_input = True

    def finish_player_name(self):
        self.leaderboard.write(self.player_name, self.current_score)
        self.write_text_on_screen("AWESOME! \n PRESS CENTRAL BUTTON TO START AGAIN " + self.leaderboard.get_highscore_string())
        self.player_name = ""
        self.reset()


    def process_gpio_buttons(self):
        global pressed
        if GPIO.input(21) and GPIO.input(22) and not pressed:
            pressed = True
            GPIO.output(26, True)
            GPIO.output(11, True)
            pygame.display.quit()
            pygame.quit()
            exit()

        if GPIO.input(22) and not pressed:
            print('Button 1')
            self.process_flashy_press(pygame.K_1)

        if GPIO.input(13) and not pressed:
            print('Button 2')
            self.process_flashy_press(pygame.K_2)

        if GPIO.input(18) and not pressed:
            print('Button 3')
            self.process_flashy_press(pygame.K_3)

        if GPIO.input(12) and not pressed:
            print('Button 4')
            self.process_flashy_press(pygame.K_4)

        if GPIO.input(5) and not pressed:
            print('Button 5')
            if not self.in_game:
                print("start game?")
                self.start_game()
            else:
                self.process_flashy_press(pygame.K_5)

        if GPIO.input(14) and not pressed:
            print('Button 6')
            self.process_flashy_press(pygame.K_6)

        if GPIO.input(17) and not pressed:
            print('Button 7')
            self.process_flashy_press(pygame.K_7)

        if GPIO.input(10) and not pressed:
            print('Button 8')
            self.process_flashy_press(pygame.K_8)

        if GPIO.input(21) and not pressed:
            print('Button 9')
            self.process_flashy_press(pygame.K_9)

    def process_flashy_press(self, key):
        global pressed
        gpio_output = KEY_TO_GPIO[key]
        pressed = True
        self.music.play(int(key) - 48)
        self.process_key_down(key)
        for each in range(0, 1):
            GPIO.output(gpio_output, True)
            sleep(0.1)
            GPIO.output(gpio_output, False)
            sleep(0.1)
        if not self.in_game:
            sleep(0.5)
        pressed = False


def main():
    gpio_setup()
    pygame.init()
    pygame.midi.init()

    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.set_instrument(0)
    player.note_on(64, 127)
    time.sleep(1)
    player.note_off(64, 127)
    del player
    pygame.midi.quit()


    try:

        clock = pygame.time.Clock()

        screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
        pygame.mouse.set_visible(0)
        font = pygame.font.Font(VISITOR_TTF_FILENAME, 50)
        masher = MakerMasher(font, screen)

        masher.write_text_on_screen("PUSH CENTRAL BUTTON")

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