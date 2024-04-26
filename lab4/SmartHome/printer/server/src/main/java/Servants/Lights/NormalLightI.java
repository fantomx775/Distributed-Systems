package Servants.Lights;

import com.zeroc.Ice.Current;

public class NormalLightI implements Demo.Light {

    private boolean isOn = false;
    @Override
    public void turnOn(Current current) {
        this.isOn = true;
    }

    @Override
    public void turnOff(Current current) {
        this.isOn = false;
    }

    @Override
    public boolean getState(Current current) {
        return this.isOn;
    }
}
