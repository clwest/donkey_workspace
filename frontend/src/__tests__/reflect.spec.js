import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import ReflectNowButton from '../components/assistant/ReflectNowButton'
import apiFetch from '../utils/apiClient'
import { vi } from 'vitest'

vi.mock('../utils/apiClient', () => ({ default: vi.fn(() => Promise.resolve({})) }))

it('opens modal and submits feedback', async () => {
  render(<ReflectNowButton slug="a" />)
  await userEvent.click(screen.getByText('Reflect Now'))
  await userEvent.type(screen.getByPlaceholderText('Your thoughts...'), 'Nice')
  await userEvent.selectOptions(screen.getByRole('combobox'), '4')
  await userEvent.click(screen.getByText('Save'))
  expect(apiFetch).toHaveBeenCalledWith('/assistants/a/reflect/', expect.any(Object))
})
