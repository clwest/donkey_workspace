import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import AssistantDashboardCard from '../components/assistant/AssistantDashboardCard'

vi.mock('../utils/apiClient', () => ({
  default: vi.fn(() => Promise.resolve({ trust_score: 80, trust_level: 'ready' }))
}))

describe('AssistantDashboardCard', () => {
  it('shows trust badge on hover', async () => {
    render(
      <AssistantDashboardCard assistant={{ id: 1, slug: 'a', name: 'Test' }} />
    )
    // trigger hover
    await screen.findByText('80/100')
    expect(screen.getByText('Trusted Agent')).toBeInTheDocument()
  })
})
