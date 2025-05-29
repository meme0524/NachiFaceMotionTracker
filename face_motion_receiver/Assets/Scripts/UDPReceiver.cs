// UDPReceiver.cs
// Description: A Unity script to receive UDP packets safely and provide access to the latest received data.

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
    public bool debugLog = true;

    private bool isRunning = true;

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
        while (isRunning)
        {
            try
            {
                byte[] data = client.Receive(ref anyIP);
                lastReceivedUDPPacket = Encoding.UTF8.GetString(data);
            }
            catch (SocketException socketEx)
            {
                if (isRunning) // ソケットが閉じられると例外が出るため
                    Debug.LogError($"SocketException: {socketEx}");
            }
            catch (System.Exception err)
            {
                Debug.LogError($"Exception: {err}");
            }
        }
    }

    void Update()
    {
        if (debugLog && !string.IsNullOrEmpty(lastReceivedUDPPacket))
        {
            //Debug.Log($"[UDPReceiver] Raw Received: [{lastReceivedUDPPacket}]");
        }
    }


    public string[] GetDataParts(char delimiter = ',')
    {
        return lastReceivedUDPPacket.Split(delimiter);
    }

    void OnApplicationQuit()
    {
        isRunning = false;
        if (client != null)
        {
            client.Close();
        }
        if (receiveThread != null && receiveThread.IsAlive)
        {
            receiveThread.Join(); // 安全に終了を待つ
        }
    }
}
