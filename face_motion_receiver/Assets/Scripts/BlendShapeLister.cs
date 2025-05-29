using UnityEngine;

public class BlendShapeLister : MonoBehaviour
{
    public SkinnedMeshRenderer faceRenderer;

    void Start()
    {
        if (faceRenderer == null)
        {
            Debug.LogError("faceRenderer ‚ªİ’è‚³‚ê‚Ä‚¢‚Ü‚¹‚ñI");
            return;
        }

        Mesh mesh = faceRenderer.sharedMesh;
        int count = mesh.blendShapeCount;

        Debug.Log($"BlendShape ‚Ì”: {count}");
        for (int i = 0; i < count; i++)
        {
            string name = mesh.GetBlendShapeName(i);
            Debug.Log($"Index {i}: {name}");
        }
    }
}
