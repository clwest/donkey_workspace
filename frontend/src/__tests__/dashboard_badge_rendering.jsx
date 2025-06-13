import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import AssistantDashboardCard from '../components/assistant/AssistantDashboardCard'

vi.mock('../utils/apiClient', () => ({
  default: vi.fn((url) => {
    if (url.includes('diagnostic_report')) {
      return Promise.resolve({
        fallback_rate: 0.1,
        glossary_success_rate: 0.8,
        avg_chunk_score: 0.67,
        rag_logs_count: 5,
      })
    }
    return Promise.resolve({ trust_score: 90, trust_level: 'ready' })
  })
}))

vi.mock('../api/assistants', () => ({
  fetchBootStatus: vi.fn(() => Promise.resolve({ has_context: true })),
  fetchDiagnosticReport: vi.fn(() => Promise.resolve({
    fallback_rate: 0.1,
    glossary_success_rate: 0.8,
    avg_chunk_score: 0.67,
    rag_logs_count: 5,
  }))
}))

describe('dashboard badge', () => {
  it('renders diagnostic badge', async () => {
    render(<AssistantDashboardCard assistant={{ id: 1, slug: 'a', name: 'Test' }} />)
    await screen.findByText(/90\/100/)
    await screen.findByText(/0.67 avg/)
    expect(screen.getByText(/80% glossary/)).toBeInTheDocument()
  })
})
