// FaceMotionReceiver.cs
// Description: Receives face expression and rotation data via UDP (JSON) and applies it to an avatar with smooth motion.

using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;
using Newtonsoft.Json.Linq;

public class FaceMotionReceiver : MonoBehaviour
{
    [Header("SkinnedMeshRenderer (Face)")]
    public SkinnedMeshRenderer faceRenderer;

    [Header("BlendShape Indices")]
    public int blinkLIndex = 1;  // Index for left eye blink blend shape
    public int blinkRIndex = 2;  // Index for right eye blink blend shape
    public int mouthIndex  = 170;

    [Header("Bone Targets")]
    public Transform headBone;

    [Header("UDP Settings")]
    public int port = 5005;

    [Header("Smoothing Settings")]
    public float blendSpeed    = 10f;
    public float rotationSpeed = 5f;

    [Header("Rotation Offset (degrees)")]
    public float yawOffset   = 0f;
    public float pitchOffset = 0f;

    [Header("Axis Inversion")]
    public bool invertYaw   = false;
    public bool invertPitch = false;

    // BlendShape weights
    private float targetBlinkL  = 0f;
    private float currentBlinkL = 0f;
    private float targetBlinkR  = 0f;
    private float currentBlinkR = 0f;
    private float targetMouth   = 0f;
    private float currentMouth  = 0f;

    // Rotation
    private Quaternion targetRotation = Quaternion.identity;

    private UdpClient client;
    private Thread receiveThread;
    private string lastJson = "";
    private readonly object lockObject = new object();

    void Start()
    {
        client = new UdpClient(port);
        receiveThread = new Thread(ReceiveData) { IsBackground = true };
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
                string text = Encoding.UTF8.GetString(data);
                lock (lockObject)
                {
                    lastJson = text;
                }
            }
            catch (SocketException e)
            {
                Debug.LogError($"UDP Receive Error: {e}");
                break;
            }
        }
    }

    void Update()
    {
        string jsonCopy;
        lock (lockObject)
        {
            jsonCopy = lastJson;
        }

        if (!string.IsNullOrEmpty(jsonCopy))
        {
            Debug.Log($"Received JSON: {jsonCopy}");
            try
            {
                var j = JObject.Parse(jsonCopy);

                // Raw flags (1=open, 0=closed)
                int flagL = j["eye"]["left"].Value<int>();
                int flagR = j["eye"]["right"].Value<int>();
                int flagM = j["mouth"].Value<int>();
                Debug.Log($"Flags - L:{flagL}, R:{flagR}, M:{flagM}");

                // Invert for blink blend shapes: 1->0 (eye open), 0->100 (eye closed)
                targetBlinkL = (1 - flagL) * 100f;
                targetBlinkR = (1 - flagR) * 100f;

                // Mouth: 1->100 (open), 0->0 (closed)
                targetMouth = flagM * 100f;
                Debug.Log($"Targets - BlinkL:{targetBlinkL}, BlinkR:{targetBlinkR}, Mouth:{targetMouth}");

                // Rotation target with offset and inversion
                float rawYaw   = j["rotation"]["yaw"].Value<float>();
                float rawPitch = j["rotation"]["pitch"].Value<float>();

                float yaw   = rawYaw + yawOffset;
                float pitch = rawPitch + pitchOffset;

                if (invertYaw)   yaw = -yaw;
                if (invertPitch) pitch = -pitch;

                Debug.Log($"Rotation - RawYaw:{rawYaw}, RawPitch:{rawPitch}");
                Debug.Log($"Rotation - AdjYaw:{yaw}, AdjPitch:{pitch}");

                targetRotation = Quaternion.Euler(pitch, yaw, 0f);
            }
            catch (System.Exception e)
            {
                Debug.LogWarning($"Failed to parse JSON: {e.Message}");
            }
        }

        // Smoothly interpolate blend shapes
        currentBlinkL = Mathf.Lerp(currentBlinkL, targetBlinkL, Time.deltaTime * blendSpeed);
        currentBlinkR = Mathf.Lerp(currentBlinkR, targetBlinkR, Time.deltaTime * blendSpeed);
        currentMouth  = Mathf.Lerp(currentMouth,  targetMouth,  Time.deltaTime * blendSpeed);

        if (faceRenderer != null)
        {
            // Swap blink mapping if blend shape indices reversed
            faceRenderer.SetBlendShapeWeight(blinkLIndex, currentBlinkR);
            faceRenderer.SetBlendShapeWeight(blinkRIndex, currentBlinkL);
            faceRenderer.SetBlendShapeWeight(mouthIndex,  currentMouth);
            Debug.Log($"Applied BlendShapes - LIdx:{blinkLIndex} Val:{currentBlinkR:F1}, RIdx:{blinkRIndex} Val:{currentBlinkL:F1}, MIdx:{mouthIndex} Val:{currentMouth:F1}");
        }

        // Smooth rotation
        if (headBone != null)
        {
            headBone.localRotation = Quaternion.Slerp(headBone.localRotation, targetRotation, Time.deltaTime * rotationSpeed);
        }
    }

    void OnApplicationQuit()
    {
        receiveThread?.Abort();
        client?.Close();
    }
}
