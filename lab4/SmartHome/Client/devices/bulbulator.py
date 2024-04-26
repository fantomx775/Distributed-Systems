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
                    buls_no = input("\nInput numbers of buls: ")
                    bulbs = self.proxy.bulbulate(int(buls_no))
                    for bul in bulbs.split(' '):
                        print(bul, end=' ')
                        time.sleep(0.1)
                case _:
                    print("Invalid action:", action)
        except Exception as e:
            print("Error:", e)

