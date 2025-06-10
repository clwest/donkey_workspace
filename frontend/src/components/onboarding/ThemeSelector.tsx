import React from 'react';

interface Props {
  theme: string;
  onChange: (value: string) => void;
}

export default function ThemeSelector({ theme, onChange }: Props) {
  return (
    <div className="btn-group mb-3">
      <button
        className={`btn ${theme === 'fantasy' ? 'btn-primary' : 'btn-outline-primary'}`}
        onClick={() => onChange('fantasy')}
      >
        🧙 Fantasy
      </button>
      <button
        className={`btn ${theme === 'practical' ? 'btn-primary' : 'btn-outline-primary'}`}
        onClick={() => onChange('practical')}
      >
        💼 Practical
      </button>
    </div>
  );
}
