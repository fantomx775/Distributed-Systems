package Utils;

import Utils.ObjectManager;

import java.util.HashMap;

public class AvailablityNotificator {
    public void notifyy(long delay){
        HashMap<String, Boolean> available_devices = new HashMap<>();
        while (true){
            try {
                available_devices = ObjectManager.getAvailableDevices();
                System.out.println("Devices availablity:");
                for (String device: available_devices.keySet()) {
                    System.out.println(device + " is " + (available_devices.get(device) ? "not in use" : "in use"));
                }
                System.out.println();
                Thread.sleep(delay);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
