// BlendShapeController.cs
// Description: Control avatar's face using BlendShape weights based on UDP data.

using UnityEngine;

public class BlendShapeController : MonoBehaviour
{
    [Header("UDP Receiver Script Reference")]
    public UDPReceiver udpReceiver;

    [Header("Skinned Mesh Renderer for Face")]
    public SkinnedMeshRenderer faceRenderer;

    [Header("BlendShape Indexes")]
    public int blinkLIndex = 0;
    public int blinkRIndex = 1;
    public int mouthIndex = 170;

    void Start()
    {
        faceRenderer.SetBlendShapeWeight(mouthIndex, 100f);
        Debug.Log("‹­§“I‚ÉŒû‚ğŠJ‚«‚Ü‚µ‚½");
    }


    void Update()
    {
        

        if (udpReceiver == null || faceRenderer == null)
        {
            Debug.LogWarning("UDPReceiver or FaceRenderer is not assigned.");
            return;
        }

        string[] parts = udpReceiver.GetDataParts(',');
        if (parts.Length < 3)
        {
            Debug.LogWarning($"Insufficient UDP data: {udpReceiver.lastReceivedUDPPacket}");
            return;
        }

        Debug.Log($"Parsed UDP: BlinkL={parts[0]}, BlinkR={parts[1]}, Mouth={parts[2]}");

        faceRenderer.SetBlendShapeWeight(blinkLIndex, parts[0] == "1" ? 100f : 0f);
        faceRenderer.SetBlendShapeWeight(blinkRIndex, parts[1] == "1" ? 100f : 0f);
        faceRenderer.SetBlendShapeWeight(mouthIndex, parts[2] == "1" ? 100f : 0f);
    }
}
