import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Arrays;

public class JavaUdpServer {

    public static void main(String args[])
    {
        System.out.println("JAVA UDP SERVER");
        DatagramSocket socket = null;
        int portNumber = 9008;

        try{
            socket = new DatagramSocket(portNumber);
            byte[] receiveBuffer = new byte[1024];

            while(true) {
                Arrays.fill(receiveBuffer, (byte)0);
                DatagramPacket receivePacket = new DatagramPacket(receiveBuffer, receiveBuffer.length);
                socket.receive(receivePacket);
                ByteBuffer buffer = ByteBuffer.wrap(receiveBuffer, 0, 4);
                buffer.order(ByteOrder.LITTLE_ENDIAN);
                int nb = buffer.getInt();
                System.out.println("received msg: " + nb);
                byte[] sendData = ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(nb + 1).array();
                DatagramPacket sendPacket = new DatagramPacket(sendData, sendData.length ,receivePacket.getAddress(), receivePacket.getPort());
                socket.send(sendPacket);
            }
        }
        catch(Exception e){
            e.printStackTrace();
        }
        finally {
            if (socket != null) {
                socket.close();
            }
        }
    }
}
