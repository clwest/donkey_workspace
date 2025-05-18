// frontend/components/ReflectionMoodFilterBar.jsx

export default function ReflectionMoodFilterBar({ moods, selectedMood, onMoodSelect }) {
    return (
      <div className="mb-4 d-flex flex-wrap justify-content-center">
        {moods.map(mood => (
          <button
            key={mood}
            onClick={() => onMoodSelect(mood)}
            className={`btn btn-sm m-1 ${selectedMood === mood ? 'btn-primary' : 'btn-outline-primary'}`}
            style={{ minWidth: "100px" }}
          >
            {mood}
          </button>
        ))}
        {selectedMood && (
          <button
            onClick={() => onMoodSelect(null)}
            className="btn btn-sm btn-secondary m-1"
            style={{ minWidth: "100px" }}
          >
            Reset
          </button>
        )}
      </div>
    );
  }