import Utils.AvailablityNotificator;
import Utils.ObjectManager;
import com.zeroc.Ice.Communicator;
import com.zeroc.Ice.ObjectAdapter;
import com.zeroc.Ice.Util;
import com.zeroc.Ice.Identity;

public class Server {
    public static void main(String[] args) {
        String endpoint = args[0];
        System.out.println("Server starting on " + endpoint);
        int status = 0;
        Communicator communicator = null;
        try {
            communicator = Util.initialize(args);
            ObjectAdapter adapter = communicator.createObjectAdapterWithEndpoints("Adapter", endpoint);

            adapter.add(ObjectManager.getLight(), new Identity("light1", "lights"));
            adapter.add(ObjectManager.getBulbulator(), new Identity("bulbulator1", "bulbulators"));
            adapter.add(ObjectManager.getDimmer(), new Identity("dimmer1", "lights"));
            adapter.add(ObjectManager.getHVAC(), new Identity("hvac1", "hvac"));

            ObjectManager.addDevice("light1");
            ObjectManager.addDevice("bulbulator1");
            ObjectManager.addDevice("dimmer1");
            ObjectManager.addDevice("hvac1");

            adapter.activate();

            System.out.println("Entering event processing loop...");

            AvailablityNotificator notificator = new AvailablityNotificator();
            Thread notificatorThread = new Thread(() -> notificator.notifyy(10000L));
            notificatorThread.start();

            communicator.waitForShutdown();
        } catch (Exception e) {
            System.err.println(e.toString());
            status = 1;
        } finally {
            if (communicator != null) {
                try {
                    communicator.destroy();
                } catch (Exception e) {
                    System.err.println(e.toString());
                    status = 1;
                }
            }
        }

        System.exit(status);
    }
}
