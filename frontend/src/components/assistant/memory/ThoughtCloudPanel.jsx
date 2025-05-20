import React from 'react';

const COLORS = {
  planning: '#0d6efd',
  reflection: '#6f42c1',
  delegation: '#20c997',
};

export default function ThoughtCloudPanel({ tagCounts = {}, onTagClick }) {
  const max = Math.max(1, ...Object.values(tagCounts));

  return (
    <div className="d-flex flex-wrap">
      {Object.entries(tagCounts).map(([tag, count]) => {
        const size = 0.8 + (count / max) * 1.2;
        const colorKey = Object.keys(COLORS).find(k => tag.startsWith(k));
        const color = COLORS[colorKey] || '#495057';
        return (
          <span
            key={tag}
            onClick={() => onTagClick && onTagClick(tag)}
            style={{
              fontSize: `${size}rem`,
              marginRight: '0.5rem',
              cursor: 'pointer',
              color,
            }}
          >
            {tag}
          </span>
        );
      })}
    </div>
  );
}
