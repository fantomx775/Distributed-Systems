import Demo

class Dimmer:
    def __init__(self, name, communicator, url):
        self.name = name
        self.communicator = communicator
        self.url = url
        self.proxy = Demo.DimmerPrx.checkedCast(communicator.stringToProxy(url))
        self.actions = {'turn on', 'turn off', 'get state', 'set brightness', 'get brightness', 'set color', 'get color'}

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
                    while True:
                        color = input("Enter color (or press Enter to quit): ")
                        if color == '':
                            print("Action canceled.")
                            break
                        try:
                            self.proxy.setColor(color)
                            break
                        except Exception as e:
                            print("Error:", e)
                case 'get color':
                    print(self.proxy.getColor())
                case _:
                    print("Invalid action:", action)

        except Exception as e:
            print("Error:", e)