
import random as rd
import time
from scipy.interpolate import interp1d
from colorama import Fore, Back, Style
import re
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
from pygame import mixer
import json
import shutil

# load the stats.txt file into a dictionairy
with open('stats.txt') as file:
    stats_string = file.read()
stats = json.loads(stats_string)

rolling = False
running = True
mixer.init()

def get_terminal_size():
    return shutil.get_terminal_size((80, 20))


def roll(dice, number, adjust, length, attributes=[]):
    rolling = True
    mixer.music.set_volume(0.25)
    mixer.music.load("click.wav")
    max_length = length #+ rd.randint(0, int(length / 2))
    sleep_time_mapping_func = interp1d([0,max_length],[1,0])

    total_minus = 0
    results = [0]*number
    if attributes != []:
        print("  ", end="") # for spacing
        for attribute in attributes:
            print('{0: >4}'.format(attribute) +'{0: <2}'.format(str(stats[attribute])), end="")
        print("")

    # the rolling loop
    while(length > 0):
        print("  ", end="") # for spacing
        print("\033[1m", end="") #makes it bold
        print("|", end="")
        print(Fore.BLACK + Back.WHITE, end="")
        for n in range(0, number):
            res = rd.randint(1, dice)
            results[n] = res
            if res == 1:
                print(Back.LIGHTGREEN_EX +'{0: >5}'.format(" " + "<o>" + " ") + Back.WHITE, end="")
            elif res == 20:
                print(Back.RED + '{0: >5}'.format(" " + str(res) + "  ") + Back.WHITE, end="")
            elif len(attributes) > n:
                if res <= stats[attributes[n]]:
                    print(Fore.GREEN + '{0: >5}'.format(" " + str(res) + "  ") + Fore.BLACK + Back.WHITE, end="")
                else:
                    print(Fore.RED + '{0: >5}'.format(" " + str(res) + "  ") + Fore.BLACK + Back.WHITE, end="")
            else:
                print('{0: >5}'.format(" " + str(res) + "  "), end="")

            print(Fore.WHITE + Back.BLACK + "|" + Fore.BLACK + Back.WHITE, end="")

        if length == 1:
            mixer.music.set_volume(0.6)

        print(Style.RESET_ALL, end="")
        mixer.music.play()

        print('\r\033[A')

        sleep_time = float(sleep_time_mapping_func(length))**15
        time.sleep(sleep_time)
        length -= 1

    # eval after rolling
    if(attributes != []):
        for n in range(0, number):
            if results[n] > stats[attributes[n]]:
                total_minus += results[n] - stats[attributes[n]]

        crit_res_chance = 1.0
        for n in range(0, number-1):
            crit_res_chance = crit_res_chance * (1/dice)

        if(len(results) == 3 and results.count("1") >= 2):
            print("\033[" + str(3 + 6*number) + "C =>" + Fore.LIGHTGREEN_EX +  " Critical Success!" + Fore.BLACK + ' (' + '{:.1%}'.format(crit_res_chance) + ")")
        elif(len(results) == 3 and results.count("20") >= 2):
            print("\033[" + str(3 + 6*number) + "C =>" + Fore.LIGHTRED_EX +  " Critical Fail!" + Fore.BLACK+ ' (' + '{:.1%}'.format(crit_res_chance) + ")")
        else:
            pass_chance = 1.0
            miss_by_this_chance = 1.0
            this_or_better_chance = 1.0
            for n in range(0, len(attributes)):
                pass_chance = pass_chance  * (stats[attributes[n]] / dice)
                miss_by_this_chance = miss_by_this_chance * (max([results[n], stats[attributes[n]]]) / dice)
                this_or_better_chance = this_or_better_chance * (results[n] / dice)


            if total_minus > 0:
                print('\033[' + str(3 + 6*number) + 'C => -' + str(total_minus) + ' (' + '{:.1%}'.format(pass_chance) + "/" + '{:.1%}'.format(miss_by_this_chance) + ")", end="")
            else:

                print('\033[' + str(3 + 6*number) + 'C => Pass!' + ' (' + '{:.1%}'.format(pass_chance) + "/" + '{:.1%}'.format(this_or_better_chance) + ")", end="")

    print("")
    rolling = False

def eval(str):
    print('\r\033[A', end="")

    xdy_regex = "^(\d)+([d]){1}(\d)*(\d)$"
    stats_roll_regex = "^(MU( )*|KL( )*|IN( )*|CH( )*|FF( )*|GE( )*|KO( )*|KK( )*|)+$"
    stats_search_regex = "(MU|KL|IN|CH|FF|GE|KO|KK){1}"

    time_delay = int(rd.gauss(50, 15))

    if str == 'q':
        running = False
        return
    elif str == "r":
        roll(20, 3, 0, time_delay)
    elif str == "h":
        print_help()
    elif str == "s":
        print_stats()
    elif re.match(xdy_regex, str):
        args = re.split("d", str)
        roll(int(args[1]), int(args[0]), 0, time_delay)
    elif re.match(stats_roll_regex, str):
        str_no_space = str.replace(" ", "")
        args = re.findall(stats_search_regex, str)
        last_roll_needs_clear = True
        roll(20, len(args), 0, time_delay, attributes=args)
    else:
        print_input_error()

def print_input_error():
    print("Invalid input: Enter h to get a list of recognized commands")

def print_help():
    options_dict = {
    "q": "quit",
    "h": "help",
    "r": "roll three 20-sided die",
    "s": "show stats (saved in stats.txt)",
    "xdy": "roll x y-sided die",
    "MU FF KK": "Roll against the selected stats"
    }
    format_str_key = '{0: >' + str(int((get_terminal_size()[0]-4)*0.25)) + '}'
    format_str_expl = '{0: <' + str(int((get_terminal_size()[0]-4)*0.75)) + '}'
    print("Recognized inputs are:")
    print("*" + ("="*(get_terminal_size()[0] - 2)) + "*")
    for key in options_dict:
        print("|" + format_str_key.format(key) + ": " + format_str_expl.format(options_dict[key]) + "|" )
    print("*" + ("="*(get_terminal_size()[0] - 2)) + "*")
    print("")

def print_stats():
    print("|", end="")
    for key in stats:
        print('{0: ^8}'.format(key + ": " + str(stats[key])), end="|")
    print("")

def clear_prev_line():
    print("\033[A\033[2K", end="")

def main():

    print_help()
    while(running):
        if(not rolling):
            eval(input())

main()
