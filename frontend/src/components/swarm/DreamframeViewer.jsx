import DreamframePlayer from "./DreamframePlayer";

export default function DreamframeViewer({ assistantId }) {
  // For now reuse DreamframePlayer which lists global segments
  return <DreamframePlayer assistantId={assistantId} />;
}
