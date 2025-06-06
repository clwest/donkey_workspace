import PropTypes from "prop-types";

const SAMPLE_TEXT = "Hello there! I'm excited to help.";

const toneStyles = {
  cheerful: "text-orange-600",
  formal: "text-blue-800",
  nerdy: "text-purple-700",
  zen: "text-green-600",
  friendly: "text-teal-600",
  mysterious: "text-gray-600 italic",
};

export default function TonePreview({ tone }) {
  const style = toneStyles[tone] || "";
  return (
    <div className={`border rounded p-2 ${style}`}>{SAMPLE_TEXT}</div>
  );
}

TonePreview.propTypes = {
  tone: PropTypes.string.isRequired,
};
