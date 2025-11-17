import { useEffect, useState } from 'react'
import { Container, Flex, Heading, Text, SegmentedControl } from '@radix-ui/themes'
import TaskGraph from './components/TaskGraph'
import { Task, Status } from './types'
import './App.css'

// Prefer explicit env, else same-origin when served statically, else localhost:8000
const API_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000')

function App() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [status, setStatus] = useState<Status | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [serverDown, setServerDown] = useState(false)
  const [debug, setDebug] = useState<boolean>(() => {
    try {
      const fromQuery = new URLSearchParams(window.location.search).get('debug')
      if (fromQuery) return fromQuery !== '0'
      const saved = localStorage.getItem('debug')
      return saved === '1'
    } catch {
      return false
    }
  })
  const [theme, setTheme] = useState<'dark' | 'light' | 'imperial'>(() => {
    const saved = localStorage.getItem('theme') as 'dark' | 'light' | 'imperial' | null
    return saved ?? 'dark'
  })
  const [rankdir, setRankdir] = useState<'LR'|'RL'|'TB'|'BT'>(() => {
    const saved = localStorage.getItem('rankdir') as any
    if (saved === 'LR' || saved === 'RL' || saved === 'TB' || saved === 'BT') return saved
    return 'TB'
  })

  const fetchData = async () => {
    try {
      setLoading(true)
      setError(null)
      setServerDown(false)

      // Fetch tasks and status in parallel
      const [tasksRes, statusRes] = await Promise.all([
        fetch(`${API_URL}/api/tasks`),
        fetch(`${API_URL}/api/status`)
      ])

      if (!tasksRes.ok || !statusRes.ok) {
        throw new Error('Failed to fetch data')
      }

      const tasksData = await tasksRes.json()
      const statusData = await statusRes.json()

      if (debug) {
        console.log('[PadAI] API_URL =', API_URL)
        console.log('[PadAI] /api/tasks →', tasksData)
        console.log('[PadAI] /api/status →', statusData)
      }

      setTasks(tasksData.tasks || [])
      setStatus(statusData)
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Unknown error'
      if (debug) console.error('[PadAI] fetch error:', err)
      setError(msg)
      // Common network error when backend is not running
      if (msg.toLowerCase().includes('failed to fetch') || msg.toLowerCase().includes('networkerror')) {
        setServerDown(true)
      }
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    // Polling disabled - use manual refresh button instead
    // TODO: Replace with WebSocket/SSE for real-time updates
  }, [])

  // Apply theme to body
  useEffect(() => {
    const body = document.body
    body.classList.remove('theme-light')
    body.classList.remove('theme-imperial')
    if (theme === 'light') body.classList.add('theme-light')
    if (theme === 'imperial') body.classList.add('theme-imperial')
    localStorage.setItem('theme', theme)
  }, [theme])

  // Persist debug flag
  useEffect(() => {
    localStorage.setItem('debug', debug ? '1' : '0')
  }, [debug])

  // Persist layout direction
  useEffect(() => {
    localStorage.setItem('rankdir', rankdir)
  }, [rankdir])

  if (loading && !tasks.length) {
    return (
      <div className="app">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">
          <h2>{serverDown ? 'Backend Unreachable' : 'Error'}</h2>
          {serverDown ? (
            <>
              <p>Cannot reach PadAI server at:</p>
              <code>{`${API_URL}`}</code>
              <p className="hint">
                Start the backend and try again:
              </p>
              <code>python main.py</code>
              <p className="hint">
                Or set <code>VITE_API_URL</code> to your server URL and reload.
              </p>
            </>
          ) : (
            <p>{error}</p>
          )}
          <button onClick={fetchData}>Retry</button>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <Container>
          <Flex align="center" justify="between" wrap="wrap" gap="3">
            <Flex align="center" gap="3">
              <Heading size="5">PadAI Dashboard</Heading>
              <button
                onClick={fetchData}
                disabled={loading}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: '1px solid var(--controls-border)',
                  background: 'var(--controls-bg)',
                  color: 'var(--controls-text)',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: loading ? 0.5 : 1,
                  fontSize: '14px'
                }}
                title="Refresh data from server"
              >
                {loading ? '⏳ Loading...' : '🔄 Refresh'}
              </button>
            </Flex>
            <div className="theme-toggle" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <SegmentedControl.Root value={theme} onValueChange={(v) => setTheme(v as any)}>
                <SegmentedControl.Item value="dark">🌙 Night</SegmentedControl.Item>
                <SegmentedControl.Item value="light">☀️ Day</SegmentedControl.Item>
                <SegmentedControl.Item value="imperial">🛰️ Imperial</SegmentedControl.Item>
              </SegmentedControl.Root>
              <SegmentedControl.Root value={rankdir} onValueChange={(v) => setRankdir(v as any)}>
                <SegmentedControl.Item value="LR">LR</SegmentedControl.Item>
                <SegmentedControl.Item value="RL">RL</SegmentedControl.Item>
                <SegmentedControl.Item value="TB">TD</SegmentedControl.Item>
                <SegmentedControl.Item value="BT">DT</SegmentedControl.Item>
              </SegmentedControl.Root>
              <label style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                <input type="checkbox" checked={debug} onChange={(e) => setDebug(e.target.checked)} />
                <Text size="2">Debug</Text>
              </label>
            </div>
          </Flex>
          {status && (
            <Flex className="status-bar" gap="5">
              <div className="status-item">
                <span className="label">Total:</span>
                <span className="value">{status.total}</span>
              </div>
              <div className="status-item ready">
                <span className="label">Ready:</span>
                <span className="value">{status.ready}</span>
              </div>
              <div className="status-item in-progress">
                <span className="label">In Progress:</span>
                <span className="value">{status.in_progress}</span>
              </div>
              <div className="status-item completed">
                <span className="label">Completed:</span>
                <span className="value">{status.completed}</span>
              </div>
            </Flex>
          )}
        </Container>
      </header>

      <main className="main">
        <div className="imperial-accent" />
        {debug && (
          <Container>
            <div style={{ margin: '12px 0', padding: 12, border: '1px dashed var(--controls-border)', borderRadius: 8 }}>
              <Text size="2">
                Debug · API: <code>{API_URL}</code> · tasks: {tasks.length} · status: {status ? 'ok' : 'n/a'}
              </Text>
            </div>
          </Container>
        )}
        <TaskGraph tasks={tasks} debug={debug} rankdir={rankdir} />
      </main>
    </div>
  )
}

export default App
