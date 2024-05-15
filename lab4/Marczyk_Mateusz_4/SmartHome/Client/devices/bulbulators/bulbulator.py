import Demo
import time
class Bulbulator:

    def __init__(self, name, communicator, url):
        self.name = name
        self.communicator = communicator
        self.url = url
        self.proxy = Demo.BulbulatorPrx.checkedCast(communicator.stringToProxy(url))
        self.actions = {'bulbulate'}

    def get_proxy(self):
        return self.proxy

    def get_actions(self):
        return self.actions

    def show_actions(self):
        print("\nAvailable actions:")
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
                case 'bulbulate':
                    while True:
                        buls_no = input("\nInput numbers of bulbs (or press Enter to quit): ")
                        if buls_no == '':
                            print("Action canceled.")
                            break
                        try:
                            buls_no = int(buls_no)
                            break
                        except ValueError:
                            print("Please enter a valid integer.")

                    if buls_no != '':
                        bulbs = self.proxy.bulbulate(buls_no)
                        for bul in bulbs.split(' '):
                            print(bul, end=' ')
                            time.sleep(0.1)

                case _:
                    print("Invalid action:", action)
        except Exception as e:
            print("Error:", e)

