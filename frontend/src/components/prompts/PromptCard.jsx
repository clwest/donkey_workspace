export default function PromptCard({ prompt }) {
    return (
      <div className="card h-100 shadow-sm">
        <div className="card-body">
          <h5 className="card-title">{prompt.title}</h5>
          <h6 className="card-subtitle mb-2 text-muted">
            {prompt.type} | {prompt.source}
          </h6>
          <p className="card-text text-muted">
            {prompt.summary || prompt.content.substring(0, 100) + "..."}
          </p>
        </div>
        <div className="card-footer">
          <small className="text-muted">{prompt.token_count || 0} tokens</small>
        </div>
      </div>
    );
  }