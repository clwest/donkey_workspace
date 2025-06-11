export default function HighContrastToggle() {
  const toggle = () => {
    document.body.classList.toggle('high-contrast');
  };
  return (
    <button
      className="btn btn-outline-secondary btn-sm me-2"
      onClick={toggle}
      aria-pressed={document.body.classList.contains('high-contrast')}
      aria-label="Toggle high contrast mode"
    >
      HC
    </button>
  );
}
