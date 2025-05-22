import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SymbolicIntegrityTag from '../../dev/SymbolicIntegrityTag';
import { analyzeThoughtIntegrity } from '../../utils/diagnostics/thoughtIntegrity';

export default function ThoughtLogCard({ thought }) {
  if (!thought) return null;

  const rawContent =
    thought.content || thought.thought || thought.summary || '';
  const integrity = analyzeThoughtIntegrity(rawContent);

  let content = rawContent.trim();
  if (integrity === 'markdown_stub') {
    content = content.replace(/```[^\n]*\n?/, '').trim();
  }

  const hasContent = content && content.length > 0;

  return (
    <div className="card mb-3">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <span className="text-xs text-gray-500">
            {thought.role || 'Assistant'} — {thought.mood || 'Neutral'}
          </span>
          {integrity !== 'valid' && <SymbolicIntegrityTag status={integrity} />}
        </div>
        {hasContent ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
        ) : (
          <em className="text-muted">[No content]</em>
        )}
      </div>
    </div>
  );
}
