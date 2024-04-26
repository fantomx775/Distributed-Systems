import sys, Ice
import Demo
from devices.bulbulator import Bulbulator
from devices.lights import Lights

def get_proxies(communicator, config_file = "config.client"):
    devices = {}
    with open(config_file) as file:
        for line in file:
            if line == "\n":
                continue
            if line.startswith("# END DEVICE DEFINITIONS"):
                break

            split = line.split('=')
            name = split[0]
            url = split[1]
            print(name, url)

            if "bulbulator" in name:
                devices['bulbulator'] = Bulbulator(name, communicator, url)
            elif "light1" in name:
                devices['light1'] = Lights(name, communicator, url)
            else:
                raise ValueError("Device", name, " not recognized.")

    return devices

with Ice.initialize(sys.argv) as communicator:
    devs = get_proxies(communicator)
    a= ''' base = communicator.stringToProxy("bulbulators/bulbulator1:tcp -h 127.0.0.2 -p 10000 -z : udp -h 127.0.0.2 -p 10000 -z")
    bb = Demo.BulbulatorPrx.checkedCast(base)
    buls = bb.bulbulate(int(10))
    print(buls) '''

    # base = communicator.stringToProxy(("lights/light1:tcp -h 127.0.0.2 -p 10000 -z : udp -h 127.0.0.2 -p 10000 -z"))
    # light = Demo.LightPrx.checkedCast(base)
    devs['light1'].get_proxy().turnOn()
    print(devs['light1'].get_proxy().getState())
    devs['light1'].get_proxy().turnOff()
    print(devs['light1'].get_proxy().getState())

    # while True:
    #     b = input()
    #     buls = devs['bulbulator'].bulbulate(int(b))
    #     print(buls)
    # devs['light1'].turnOn()
    # state = devs.getState()
    # print(state)
    # devs['light1'].turnOff()
    # state = devs.getState()

if __name__ == "__main__":
    with Ice.initialize(sys.argv) as communicator:
        devices = get_proxies(communicator)
        if not devices:
            print("[ERROR] No active proxies found")
            exit(1)

        print("Client ready, entering processing loop.")

        print("\n[USAGE] type device name to make operation")
        print("[EXIT] type 'exit' or 'quit' to exit")

        while True:
            print("\nAvailable devices:")
            for device_name in devices:
                print(device_name)
            selected_device = input("\nSelect device: ")
            if selected_device.strip().lower() in {'exit', 'quit'}:
                print('EXITING...')
                exit(0)
            if selected_device not in devices:
                print("Unknown device. Did you make a typo?\n")
                continue
            devices[selected_device].show_actions()
            action = input(f'[{selected_device}] => ')
            if not action:
                continue
            if action.strip() not in devices[selected_device].actions:
                print(f'\n[{selected_device}] Unknown action\n')
                continue

            try:
                devices[selected_device].execute_action(action.strip())
            except Exception as e:
                print(e)
