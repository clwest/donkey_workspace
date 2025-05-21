import { useState } from "react";
import { generateImage } from "../../utils/apiClient";

export default function ImageCreatePage() {
  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await generateImage({ prompt });
      setImage(data);
    } catch (err) {
      console.error("Failed to generate image", err);
      setError("Generation failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container py-4">
      <h1 className="mb-4">🎨 Create Image</h1>
      <div className="mb-3">
        <textarea
          className="form-control"
          rows="3"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter image prompt..."
        />
      </div>
      <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate"}
      </button>
      {error && <p className="text-danger mt-2">{error}</p>}
      {image?.output_url && (
        <div className="mt-4">
          <img src={image.output_url} alt="generated" className="img-fluid" />
        </div>
      )}
    </div>
  );
}
