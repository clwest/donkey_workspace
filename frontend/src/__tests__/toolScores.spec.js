import { render, screen } from '@testing-library/react'
import ToolScoreTable from '../components/assistants/ToolScoreTable'

test('renders tool score rows', () => {
  const scores = [
    { tool: { id: 1, name: 'Echo' }, usage_count: 3, confidence: 0.8, tags: ['efficiency'] }
  ]
  render(<ToolScoreTable scores={scores} />)
  expect(screen.getByText('Echo')).toBeInTheDocument()
  expect(screen.getByText('3')).toBeInTheDocument()
})
