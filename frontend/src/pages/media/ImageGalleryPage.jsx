import { useEffect, useState } from "react";
import { fetchImages } from "../../utils/apiClient";

export default function ImageGalleryPage() {
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadImages() {
      try {
        const data = await fetchImages();
        const results = data.results || data;
        setImages(results);
      } catch (err) {
        console.error("Failed to load images", err);
      } finally {
        setLoading(false);
      }
    }
    loadImages();
  }, []);

  return (
    <div className="container py-4">
      <h1 className="mb-4">🖼 Image Gallery</h1>
      {loading ? (
        <p className="text-muted">Loading...</p>
      ) : images.length === 0 ? (
        <p className="text-muted">No images found.</p>
      ) : (
        <div className="row">
          {images.map((img) => (
            <div key={img.id} className="col-md-3 mb-3">
              {img.output_url && (
                <img src={img.output_url} alt="generated" className="img-fluid" />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
