package Servants.Bulbulator;

import Utils.ObjectManager;
import com.zeroc.Ice.Current;

import java.util.UUID;
import java.util.concurrent.locks.ReentrantLock;

public class BulbulatorI implements Demo.Bulbulator
{
    private String UUID;

    private ReentrantLock lock;
    private String name;
    private boolean isOn = false;

    public BulbulatorI(String name)
    {
        this.lock = new ReentrantLock();
        this.name = name;
        this.UUID = java.util.UUID.randomUUID().toString();
    }

    @Override
    public String bulbulate(int b, Current current) {
        this.lock.lock();
        ObjectManager.setAvailability(name, false);
        String bulbulation = "";
        long delay = 500L * b;
        while(b > 0) {
            bulbulation += "bul ";
            b--;
        }
        System.out.println(bulbulation);
        try {
            Thread.sleep(delay);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
        System.out.println("Bulbulation finished");
        this.lock.unlock();
        ObjectManager.setAvailability(name, true);
        return bulbulation != null ? bulbulation : "";
    }

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
