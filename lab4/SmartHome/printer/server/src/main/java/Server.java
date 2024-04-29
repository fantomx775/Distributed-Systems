import Servants.Bulbulator.BulbulatorI;
import Servants.Lights.DimmerI;
import Servants.Lights.NormalLightI;
import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;
import com.zeroc.Ice.Identity;


public class Server
{
    public static void main(String[] args)
    {
        try(Communicator communicator = Util.initialize(args))
        {
            ObjectAdapter adapter = communicator.createObjectAdapterWithEndpoints("Adapter", "tcp -h 127.0.0.2 -p 10000 -z : udp -h 127.0.0.2 -p 10000 -z");

            BulbulatorI bulbulator = new BulbulatorI();
            NormalLightI light = new NormalLightI();
            DimmerI dimmer = new DimmerI();

            adapter.add(light, new Identity("light1", "lights"));
            adapter.add(bulbulator, new Identity("bulbulator1", "bulbulators"));
            adapter.add(dimmer, new Identity("dimmer1", "lights"));
            adapter.activate();

            System.out.println("Entering event processing loop...");
            communicator.waitForShutdown();
        }

    }
}