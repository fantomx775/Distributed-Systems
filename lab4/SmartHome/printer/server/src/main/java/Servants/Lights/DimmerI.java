package Servants.Lights;

import Demo.Color;
import com.zeroc.Ice.Current;

public class DimmerI implements Demo.DimmerDisp {

    private boolean isOn = false;
    private int brightness = 0;
    private Color color = Color.RED;

    @Override
    public void turnOn(Current current) {
        isOn = true;
        System.out.println("Dimmer light turned on.");
    }

    @Override
    public void turnOff(Current current) {
        isOn = false;
        System.out.println("Dimmer light turned off.");
    }

    @Override
    public boolean getState(Current current) {
        return isOn;
    }

    @Override
    public void setBrightness(int b, Current current) {
        brightness = b;
        System.out.println("Brightness set to: " + brightness);
    }

    @Override
    public int getBrightness(Current current) {
        return brightness;
    }

    @Override
    public void setColor(Color c, Current current) {
        color = c;
        System.out.println("Color set to: " + color);
    }

    @Override
    public Color getColor(Current current) {
        return color;
    }
}
