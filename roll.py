
import random as rd
import time
from scipy.interpolate import interp1d
from colorama import Fore, Back, Style
import re
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import mixer

rolling = False
running = True
mixer.init()

def roll(dice, number, adjust, length):
    mixer.music.set_volume(0.25)
    mixer.music.load("click.wav")
    max_length = length #+ rd.randint(0, int(length / 2))
    sleep_time_mapping_func = interp1d([0,max_length],[1,0])
    while(length > 0):
        print("  |", end="")
        for n in range(0, number):
            res = rd.randint(1, dice)
            print(Fore.BLACK + Back.WHITE + '\033[1m', end= "")
            if res == 1:
                print('{0: >5}'.format(" " + "<o>" + " "), end="")
            else:
                print('{0: >5}'.format(" " + str(res) + "  "), end="")
            print(Style.RESET_ALL, end="|")

        if length == 1:
                mixer.music.set_volume(0.6)
        mixer.music.play()

        if(adjust != 0):
            if(adjust < 0):
                print(' - ' + str(abs(adjust)), end="")
            else:
                print(' + ' + str(adjust), end="")

        print('\r\033[A')
        sleep_time = float(sleep_time_mapping_func(length))**15
        time.sleep(sleep_time)
        length -= 1

    print("")

def eval(str):
    print('\r\033[A', end="")
    if str == 'q':
        running = False
        return
    elif str == "r":
        roll(20, 3, 0, rd.randint(50, 150))
        return
    args = re.split("d|[+-]| [+-] ", str)
    try:
        if len(args) == 2:
            adjust = 0
        else:
            adjust = int(args[2])
        rolling = True
        roll(int(args[1]), int(args[0]), adjust, int(rd.gauss(75, 10)))
        rolling = False
    except:
        print("Invalid input")


def main():
    print("r to roll 3 d20")
    print("'xdy' to roll x die with y sides")
    while(running):
        if(not rolling):
            eval(input())

main()
