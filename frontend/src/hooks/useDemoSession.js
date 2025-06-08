import { useState } from 'react'

export default function useDemoSession() {
  const [demoSessionId] = useState(() => {
    const key = 'demo_session_id'
    const stored = localStorage.getItem(key)
    if (stored) return stored
    const id = crypto.randomUUID()
    localStorage.setItem(key, id)
    return id
  })

  return { demoSessionId }
}
