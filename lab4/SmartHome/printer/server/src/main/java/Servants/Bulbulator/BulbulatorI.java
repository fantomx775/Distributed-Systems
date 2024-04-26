package Servants.Bulbulator;

import com.zeroc.Ice.Current;

public class BulbulatorI implements Demo.Bulbulator
{

    @Override
    public String bulbulate(int b, Current current) {
        String bulbulation = "";
        while(b > 0) {
            bulbulation += "bul ";
            b--;
        }
        System.out.println(bulbulation);
        return bulbulation != null ? bulbulation : "";
    }
}
