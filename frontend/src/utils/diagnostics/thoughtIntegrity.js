export function analyzeThoughtIntegrity(content) {
  if (!content || content.trim().length < 10) return 'empty';
  if (content.includes('```json') && !content.includes('{')) return 'markdown_stub';
  if (content.toLowerCase().includes('error') || content.includes('traceback')) return 'error_log';
  return 'valid';
}
