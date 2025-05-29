using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class UDPReceiver : MonoBehaviour
{
    UdpClient client;
    Thread receiveThread;
    public int port = 5005;
    public string lastReceivedUDPPacket = "";

    void Start()
    {
        client = new UdpClient(port);
        receiveThread = new Thread(new ThreadStart(ReceiveData));
        receiveThread.IsBackground = true;
        receiveThread.Start();
    }

    void ReceiveData()
    {
        IPEndPoint anyIP = new IPEndPoint(IPAddress.Any, port);
        while (true)
        {
            try
            {
                byte[] data = client.Receive(ref anyIP);
                lastReceivedUDPPacket = Encoding.UTF8.GetString(data);
            }
            catch (System.Exception err)
            {
                Debug.LogError(err.ToString());
            }
        }
    }

    void Update()
    {
        Debug.Log($"Received: {lastReceivedUDPPacket}");
    }

    void OnApplicationQuit()
    {
        receiveThread.Abort();
        client.Close();
    }
}
