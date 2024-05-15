package Servants.Lights;

import Demo.Color;
import Demo.UnsupportedColorException;
import Demo.ValueOutOfRangeException;
import Utils.ExceptionManager;
import com.zeroc.Ice.Current;

import java.util.concurrent.locks.ReentrantLock;

public class DimmerI implements Demo.LightController {
    private String UUID;

    private ReentrantLock lock;
    private String name;
    private boolean isOn = false;
    private int brightness = 50;
    private Color color = Color.RED;

    public DimmerI(String name) {
        this.lock = new ReentrantLock();
        this.name = name;
        this.UUID = java.util.UUID.randomUUID().toString();
    }

    public void turnOn(Current current) {
        this.lock.lock();
        isOn = true;
        System.out.println("Dimmer light turned on.");
        this.lock.unlock();
    }

    public void turnOff(Current current) {
        this.lock.lock();
        isOn = false;
        System.out.println("Dimmer light turned off.");
        this.lock.unlock();
    }

    public boolean getState(Current current) {
        this.lock.lock();
        boolean state = isOn;
        this.lock.unlock();
        return state;
    }

    @Override
    public void setBrightness(int b, Current current) {
        this.lock.lock();
        try {
            ExceptionManager.valueOutOfRangeException(0, 100, b);
            this.brightness = b;
            System.out.println("Brightness set to: " + brightness);
        } catch (ValueOutOfRangeException e) {
            System.err.println("Error: " + e.getMessage());
            throw new RuntimeException("Brightness value out of range. Must be between 0 and 100.", e);
        } finally {
            this.lock.unlock();
        }
    }


    @Override
    public int getBrightness(Current current) {
        this.lock.lock();
        int bright = brightness;
        this.lock.unlock();
        return bright;
    }

    @Override
    public void setColor(Color c, Current current) {
        this.lock.lock();
        try {
            ExceptionManager.unsupportedColorException(c);
            color = c;
            System.out.println("Color set to: " + color);
        } catch (UnsupportedColorException e) {
            System.err.println("Error: " + e.getMessage());
            throw new RuntimeException("Unsupported color: " + c, e);
        } finally {
            this.lock.unlock();
        }
    }


    @Override
    public Color getColor(Current current) {
        this.lock.lock();
        Color col = color;
        this.lock.unlock();
        return col;
    }
}
