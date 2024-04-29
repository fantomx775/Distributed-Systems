import Demo

class Lights:
    def __init__(self, name, communicator, url):
        self.name = name
        self.communicator = communicator
        self.url = url
        self.proxy = Demo.LightPrx.checkedCast(communicator.stringToProxy(url))
        self.actions = {'turn on', 'turn off', 'get state'}

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
                case _:
                    print("Invalid action:", action)
        except Exception as e:
            print("Error:", e)