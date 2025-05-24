import RelayChainNodeCard from "./RelayChainNodeCard";

export default function RelayChainViewer({ chain }) {
  if (!chain) return null;

  return (
    <div>
      {chain.nodes.map((node, idx) => (
        <div key={node.id || idx}>
          <RelayChainNodeCard node={node} />
          {idx < chain.nodes.length - 1 && (
            <div className="text-center my-2">⬇️</div>
          )}
        </div>
      ))}
    </div>
  );
}
