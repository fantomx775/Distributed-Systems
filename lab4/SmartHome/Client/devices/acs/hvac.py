import Demo

import Printer_ice
from Printer_ice import _M_Demo
class HVAC:
    def __init__(self, name, communicator, url):
        self.name = name
        self.communicator = communicator
        self.url = url
        self.proxy = Demo.HVACPrx.checkedCast(communicator.stringToProxy(url))
        self.actions = {
            'turn on',
            'turn off',
            'get state',
            'set temperature',
            'get temperature',
            'set humidity',
            'get humidity',
            'set fragrances',
            'get fragrances',
            'schedule',
            'get schedules'
        }

        self.fragrances = {
        'LAVENDER' : _M_Demo.Fragrance.LAVENDER,
        'CITRUS' : _M_Demo.Fragrance.CITRUS,
        'VANILLA' : _M_Demo.Fragrance.VANILLA,
        'ROSE' : _M_Demo.Fragrance.ROSE,
        'OCEAN' : _M_Demo.Fragrance.OCEAN,
        'FRESHLINEN' : _M_Demo.Fragrance.FRESHLINEN,
        'SANDALWOOD' : _M_Demo.Fragrance.SANDALWOOD,
        'JASMINE' : _M_Demo.Fragrance.JASMINE,
        'PEPPERMINT' : _M_Demo.Fragrance.PEPPERMINT,
        'EUCALYPTUS' : _M_Demo.Fragrance.EUCALYPTUS,
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

    def set_temperature(self):
        while True:
            temperature = input("Enter temperature (13-30 *C) (or press Enter to quit): ")
            if temperature == '':
                print("Action canceled.")
                break
            try:
                temperature = int(temperature)
                if 13 <= temperature <= 30:
                    return temperature
                else:
                    print("Please enter a temperature between 13 and 30 degrees.")
            except ValueError:
                print("Please enter a valid integer.")

    def set_humidity(self):
        while True:
            humidity = input("Enter humidity (20-80) (or press Enter to quit): ")
            if humidity == '':
                print("Action canceled.")
                break
            try:
                humidity = int(humidity)
                if 20 <= humidity <= 80:
                    return humidity
                else:
                    print("Please enter a humidity between 20 and 80 degrees.")
            except ValueError:
                print("Please enter a valid integer.")

    def set_fragrances(self):
        print("Available fragrances:")
        for fragrance in self.fragrances:
            print(fragrance)
        while True:
            fragrance_input = input("Enter fragrances, separated by space (or press Enter to quit): ")
            if fragrance_input == '':
                print("Action canceled.")
                break
            fragrances = fragrance_input.split(' ')
            fragrances_set = set(fragrances) & set(self.fragrances.keys())
            if fragrances_set:
                try:
                    return fragrances_set
                except Exception as e:
                    print("Error:", e)
            else:
                print("Invalid fragrances. Please choose from the available fragrances.")

    def check_time(self, time):
        try:
            time = time.split('-')
            if len(time) == 2:
                if 0 <= int(time[0]) <= 23 and 0 <= int(time[1]) <= 59:
                    return True
                else:
                    return False
            else:
                return False
        except ValueError:
            return False
    def set_time(self, string):
        while True:
            time = input(f"Enter {string} time (HH-MM) (or press Enter to quit): ")
            if time == '':
                print("Action canceled.")
                break
            try:
                if(self.check_time(time)):
                    return time
                else:
                    raise ValueError
            except ValueError:
                print("Please enter a valid date.")

    def execute_action(self, action):
        try:
            match action:
                case 'turn on':
                    self.proxy.turnOn()

                case 'turn off':
                    self.proxy.turnOff()

                case 'get state':
                    print(self.proxy.getState())

                case 'set temperature':
                   temperature = self.set_temperature()
                   if temperature:
                    self.proxy.setTemperature(temperature)

                case 'get temperature':
                    print(self.proxy.getTemperature())

                case 'set humidity':
                    humidity = self.set_humidity()
                    if humidity:
                        self.proxy.setHumidity(humidity)

                case 'get humidity':
                    print(self.proxy.getHumidity())

                case 'set fragrances':
                    fragrances = self.set_fragrances()
                    if fragrances:
                        f_arg = []
                        for fragrance in fragrances:
                            f_arg.append(self.fragrances[fragrance])
                        self.proxy.setFragrances(f_arg)
                    else:
                        print("Invalid fragrances")

                case 'get fragrances':
                    print(self.proxy.getFragrances())

                case 'schedule':
                    temperature = self.set_temperature()
                    if not temperature:
                        return

                    humidity = self.set_humidity()
                    if not humidity:
                        return

                    fragrances = self.set_fragrances()
                    if not fragrances:
                        return
                    else:
                        f_arg = []
                        for fragrance in fragrances:
                            f_arg.append(self.fragrances[fragrance])

                    start_time = self.set_time("start")
                    if not start_time:
                        return

                    end_time = self.set_time("end")
                    if not end_time:
                        return

                    self.proxy.addSchedule(_M_Demo.ScheduleBlock(start_time, end_time, temperature, humidity, f_arg))

                case 'get schedules':
                    print(self.proxy.getSchedules())

                case _:
                    print("Invalid action:", action)

        except Exception as e:
            print("Error:", e)