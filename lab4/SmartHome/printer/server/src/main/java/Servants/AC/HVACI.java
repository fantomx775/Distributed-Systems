package Servants.AC;

import Demo.*;
import Utils.ExceptionManager;
import com.zeroc.Ice.Current;

import java.util.concurrent.locks.ReentrantLock;

public class HVACI implements HVAC{
    private String UUID;

    private ReentrantLock lock;
    private String name;
    private boolean busy;

    private boolean isOn = false;
    private int temperature = 20;
    private int humidity = 50;
    private Fragrance[] fragrances = new Fragrance[0];

    private ScheduleBlock[] schedules = new ScheduleBlock[0];

    public HVACI(String name)
    {
        this.lock = new ReentrantLock();
        this.name = name;
        this.busy = false;
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

    @Override
    public void setTemperature(int t, Current current) {
        this.lock.lock();
        try {
            ExceptionManager.valueOutOfRangeException(13, 30, t);
            this.temperature = t;
        } catch (ValueOutOfRangeException e) {
            e.printStackTrace();
        } finally {
            this.lock.unlock();
        }
    }

    @Override
    public int getTemperature(Current current) {
        this.lock.lock();
        int temp = this.temperature;
        this.lock.unlock();
        return temp;
    }

    @Override
    public void setHumidity(int h, Current current) {
        this.lock.lock();
        try {
            ExceptionManager.valueOutOfRangeException(20, 80, h);
            this.humidity = h;
        } catch (ValueOutOfRangeException e) {
            e.printStackTrace();
        } finally {
            this.lock.unlock();
        }
    }

    @Override
    public int getHumidity(Current current) {
        this.lock.lock();
        int hum = this.humidity;
        this.lock.unlock();
        return hum;
    }

    @Override
    public void setFragrances(Fragrance[] f, Current current) {
        this.lock.lock();
        try{
            for (Fragrance fragrance : f) {
                ExceptionManager.unsupportedFragranceException(fragrance);
            }
            this.fragrances = f;
        } catch (UnsupportedFragranceException e) {
            e.printStackTrace();
        } finally {
            this.lock.unlock();
        }
    }

    @Override
    public Fragrance[] getFragrances(Current current) {
        this.lock.lock();
        Fragrance[] fr = this.fragrances;
        this.lock.unlock();
        return fr;
    }

    @Override
    public void addSchedule(ScheduleBlock s, Current current)  {
        this.lock.lock();
        try {
            ScheduleBlock[] newSchedules = new ScheduleBlock[this.schedules.length + 1];
            for (int i = 0; i < this.schedules.length; i++) {
                newSchedules[i] = this.schedules[i];
            }

            ExceptionManager.valueOutOfRangeException(13, 30, s.temperature);
            ExceptionManager.valueOutOfRangeException(20, 80, s.humidity);
            for (Fragrance fragrance : s.fragrances) {
                ExceptionManager.unsupportedFragranceException(fragrance);
            }

            newSchedules[this.schedules.length] = s;
            this.schedules = newSchedules;
        } catch (UnsupportedFragranceException | ValueOutOfRangeException e) {
            e.printStackTrace();
        } finally {
            this.lock.unlock();
        }
    }

    @Override
    public ScheduleBlock[] getSchedules(Current current) {
        this.lock.lock();
        ScheduleBlock[] sch = this.schedules;
        this.lock.unlock();
        return sch;
    }
}
