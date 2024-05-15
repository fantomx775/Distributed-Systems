package Utils;

import Servants.AC.HVACI;
import Servants.Bulbulator.BulbulatorI;
import Servants.Lights.DimmerI;
import Servants.Lights.NormalLightI;

import java.util.ArrayList;
import java.util.HashMap;

public class ObjectManager {

    private static HashMap<String, Boolean> availableDevices = new HashMap<>();
    private static BulbulatorI bulbulator = new BulbulatorI("bulbulator1");
    private static NormalLightI light = new NormalLightI("light1");
    private static DimmerI dimmer = new DimmerI("dimmer1");
    private static HVACI hvac = new HVACI("hvac1");

    public static void addDevice(String deviceName) {
        availableDevices.put(deviceName, true);
    }

    public static void removeDevice(String deviceName) {
        availableDevices.remove(deviceName);
    }

    public static void setAvailability(String deviceName, boolean isAvailable) {
        if (availableDevices.containsKey(deviceName)) {
            availableDevices.put(deviceName, isAvailable);
        }
    }

    public static HashMap<String, Boolean> getAvailableDevices() {
        return availableDevices;
    }

    public static BulbulatorI getBulbulator() {
        return bulbulator;
    }

    public static NormalLightI getLight() {
        return light;
    }

    public static DimmerI getDimmer() {
        return dimmer;
    }

    public static HVACI getHVAC() {
        return hvac;
    }
}
