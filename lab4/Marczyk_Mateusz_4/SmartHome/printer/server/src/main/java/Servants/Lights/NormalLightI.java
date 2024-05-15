package Servants.Lights;

import com.zeroc.Ice.Current;

import java.util.concurrent.locks.ReentrantLock;

public class NormalLightI implements Demo.Light {
    private String UUID;

    private ReentrantLock lock;
    private String name;

    private boolean isOn = false;

    public NormalLightI(String name)
    {
        this.lock = new ReentrantLock();
        this.name = name;
        this.UUID = java.util.UUID.randomUUID().toString();
    }
    @Override
    public void turnOn(Current current) {
        this.lock.lock();
        this.isOn = true;
        this.lock.unlock();
    }

    @Override
    public void turnOff(Current current) {
        this.lock.lock();
        this.isOn = false;
        this.lock.unlock();
    }

    @Override
    public boolean getState(Current current) {
        this.lock.lock();
        boolean state = this.isOn;
        this.lock.unlock();
        return state;
    }
}
