import Demo
from colorama import init, Fore

import Printer_ice
from Printer_ice import _M_Demo


class Dimmer:
    def __init__(self, name, communicator, url):
        self.name = name
        self.communicator = communicator
        self.url = url
        self.proxy = Demo.LightControllerPrx.checkedCast(communicator.stringToProxy(url))
        self.actions = {'turn on', 'turn off', 'get state', 'set brightness', 'get brightness', 'set color', 'get color'}
        self.colors = {
            'RED': _M_Demo.Color.RED,
            'GREEN': _M_Demo.Color.GREEN,
            'BLUE': _M_Demo.Color.BLUE,
            'YELLOW': _M_Demo.Color.YELLOW,
            'PURPLE': _M_Demo.Color.PURPLE,
            'ORANGE': _M_Demo.Color.ORANGE,
            'WHITE': _M_Demo.Color.WHITE,
            'PINK': _M_Demo.Color.PINK,
            'CYAN': _M_Demo.Color.CYAN,
            'LIME': _M_Demo.Color.LIME,
        }

    def get_proxy(self):
        return self.proxy

    def get_actions(self):
        return self.actions

    def show_actions(self):
        print("Available actions:\n")
        for action in self.actions:
            print(action)
        print()

    def execute_action(self, action):
        try:
            match action:
                case 'turn on':
                    self.proxy.turnOn()
                case 'turn off':
                    self.proxy.turnOff()
                case 'get state':
                    print(self.proxy.getState())
                case 'set brightness':
                    while True:
                        brightness = input("Enter brightness (0-100) (or press Enter to quit): ")
                        if brightness == '':
                            print("Action canceled.")
                            break
                        try:
                            brightness = int(brightness)
                            if 0 <= brightness <= 100:
                                self.proxy.setBrightness(brightness)
                                break
                            else:
                                print("Please enter a number between 0 and 100.")
                        except ValueError:
                            print("Please enter a valid integer.")
                case 'get brightness':
                    print(self.proxy.getBrightness())
                case 'set color':
                    print("Available colors:")
                    for color in self.colors:
                        if color.upper() == 'RED':
                            print(f"{Fore.RED}{color}{Fore.RESET}")
                        elif color.upper() == 'GREEN':
                            print(f"{Fore.GREEN}{color}{Fore.RESET}")
                        elif color.upper() == 'BLUE':
                            print(f"{Fore.BLUE}{color}{Fore.RESET}")
                        elif color.upper() == 'YELLOW':
                            print(f"{Fore.YELLOW}{color}{Fore.RESET}")
                        elif color.upper() == 'PURPLE':
                            print(f"{Fore.MAGENTA}{color}{Fore.RESET}")
                        elif color.upper() == 'ORANGE':
                            print(f"{Fore.LIGHTRED_EX}{color}{Fore.RESET}")
                        elif color.upper() == 'WHITE':
                            print(f"{color}")
                        elif color.upper() == 'PINK':
                            print(f"{Fore.LIGHTMAGENTA_EX}{color}{Fore.RESET}")
                        elif color.upper() == 'CYAN':
                            print(f"{Fore.CYAN}{color}{Fore.RESET}")
                        elif color.upper() == 'LIME':
                            print(f"{Fore.LIGHTGREEN_EX}{color}{Fore.RESET}")

                    while True:
                        color_input = input("Enter color (or press Enter to quit): ")
                        if color_input == '':
                            print("Action canceled.")
                            break
                        elif color_input.upper() in self.colors:
                            try:
                                self.proxy.setColor(self.colors[color_input])
                                break
                            except Exception as e:
                                print("Error:", e)
                        else:
                            print("Invalid color. Please choose from the available colors.")

                case 'get color':
                    print(self.proxy.getColor())
                case _:
                    print("Invalid action:", action)

        except Exception as e:
            print("Error:", e)