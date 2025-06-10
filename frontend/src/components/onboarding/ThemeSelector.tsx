import React from 'react';

interface Props {
  specialty: string;
  onChange: (value: string) => void;
}

export default function ThemeSelector({ specialty, onChange }: Props) {
  return (
    <div className="btn-group mb-3">
      <button
        className={`btn ${specialty === 'fantasy' ? 'btn-primary' : 'btn-outline-primary'}`}
        onClick={() => onChange('fantasy')}
      >
        🧙 Fantasy
      </button>
      <button
        className={`btn ${specialty === 'practical' ? 'btn-primary' : 'btn-outline-primary'}`}
        onClick={() => onChange('practical')}
      >
        💼 Practical
      </button>
    </div>
  );
}
