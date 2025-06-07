import { describe, it, expect, beforeEach, vi } from 'vitest'
import { loginUser, refreshToken, logoutUser } from '../api/auth'

// mock fetch
global.fetch = vi.fn()

function mockResponse(data) {
  return Promise.resolve({ ok: true, json: async () => data })
}

beforeEach(() => {
  localStorage.clear()
  fetch.mockReset()
})

describe('auth flow', () => {
  it('login stores tokens', async () => {
    fetch.mockImplementation(() => mockResponse({ access: 'a', refresh: 'r' }))
    await loginUser('user', 'pw')
    expect(localStorage.getItem('access')).toBe('a')
    expect(localStorage.getItem('refresh')).toBe('r')
  })

  it('refresh updates tokens', async () => {
    localStorage.setItem('refresh', 'r')
    fetch.mockImplementation(() => mockResponse({ access: 'b', refresh: 'newr' }))
    await refreshToken()
    expect(fetch).toHaveBeenCalled()
    expect(localStorage.getItem('access')).toBe('b')
    expect(localStorage.getItem('refresh')).toBe('newr')
  })

  it('logout clears tokens', () => {
    localStorage.setItem('access', 'a')
    localStorage.setItem('refresh', 'r')
    logoutUser()
    expect(localStorage.getItem('access')).toBeNull()
    expect(localStorage.getItem('refresh')).toBeNull()
  })
})
