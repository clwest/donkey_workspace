import { useEffect, useState } from "react";
import { fetchCharacters } from "../../utils/apiClient";
import { Link } from "react-router-dom";

export default function CharacterListPage() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCharacters() {
      try {
        const data = await fetchCharacters();
        const results = data.results || data;
        setCharacters(results);
      } catch (err) {
        console.error("Failed to load characters", err);
      } finally {
        setLoading(false);
      }
    }
    loadCharacters();
  }, []);

  return (
    <div className="container py-4">
      <h1 className="mb-4">🎭 Characters</h1>
      {loading ? (
        <p className="text-muted">Loading...</p>
      ) : characters.length === 0 ? (
        <p className="text-muted">No characters found.</p>
      ) : (
        <div className="row">
          {characters.map((c) => (
            <div key={c.id} className="col-md-4 mb-3">
              <div className="card h-100">
                {c.image_url && (
                  <img src={c.image_url} className="card-img-top" alt={c.name} />
                )}
                <div className="card-body">
                  <h5 className="card-title">{c.name}</h5>
                  {c.description && <p className="card-text">{c.description}</p>}
                  {c.scene_images && c.scene_images.length > 0 && (
                    <img
                      src={c.scene_images[0].output_url}
                      alt="scene"
                      className="img-fluid"
                    />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
