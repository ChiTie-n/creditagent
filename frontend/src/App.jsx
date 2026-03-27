import { useEffect, useMemo, useState } from 'react'
import LeftSidebar from './components/LeftSidebar'
import AgentFlow from './components/AgentFlow'
import ResultSidebar from './components/ResultSidebar'
import './index.css'

const EMPTY_SESSION = {
  steps: [],
  thoughts: [],
  llmStatus: null,
  agenticMode: 'react_llm',
}

export default function App() {
  const [selectedBorrower, setSelectedBorrower] = useState(null)
  const [resultsByBorrower, setResultsByBorrower] = useState({})
  const [sessionsByBorrower, setSessionsByBorrower] = useState({})
  const [runningBorrower, setRunningBorrower] = useState(null)
  const [selectedProfile, setSelectedProfile] = useState(null)
  const [viewportWidth, setViewportWidth] = useState(() => window.innerWidth)
  const [mobilePanel, setMobilePanel] = useState('borrowers')

  const currentSession = useMemo(
    () => (selectedBorrower && sessionsByBorrower[selectedBorrower]) || EMPTY_SESSION,
    [selectedBorrower, sessionsByBorrower]
  )
  const currentResult = selectedBorrower ? resultsByBorrower[selectedBorrower] || null : null
  const isRunning = runningBorrower !== null
  const isMobile = viewportWidth < 960

  useEffect(() => {
    const handleResize = () => setViewportWidth(window.innerWidth)
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  useEffect(() => {
    if (!isMobile) {
      setMobilePanel('borrowers')
      return
    }
    if (mobilePanel === 'result' && !currentResult) {
      setMobilePanel(selectedBorrower ? 'workflow' : 'borrowers')
    }
  }, [isMobile, mobilePanel, currentResult, selectedBorrower])

  useEffect(() => {
    if (!selectedBorrower) {
      setSelectedProfile(null)
      return
    }

    fetch(`/personas/${selectedBorrower}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => setSelectedProfile(data))
      .catch(() => setSelectedProfile(null))
  }, [selectedBorrower])

  const handleRun = (borrowerId) => {
    setSelectedBorrower(borrowerId)
    setRunningBorrower(borrowerId)
    if (isMobile) setMobilePanel('workflow')
    setSessionsByBorrower(prev => ({
      ...prev,
      [borrowerId]: {
        steps: [],
        thoughts: [],
        llmStatus: null,
        agenticMode: null,
      },
    }))

    const eventSource = new EventSource(`/assess/stream/${borrowerId}`)

    eventSource.onmessage = (e) => {
      const data = JSON.parse(e.data)

      switch (data.type) {
        case 'llm_status':
          setSessionsByBorrower(prev => ({
            ...prev,
            [borrowerId]: {
              ...(prev[borrowerId] || EMPTY_SESSION),
              llmStatus: data.status,
            },
          }))
          break

        case 'thought':
          setSessionsByBorrower(prev => {
            const session = prev[borrowerId] || EMPTY_SESSION
            return {
              ...prev,
              [borrowerId]: {
                ...session,
                llmStatus: null,
                thoughts: [
                  ...session.thoughts,
                  {
                    content: data.content,
                    agent: data.agent,
                    ts: data.ts,
                  },
                ],
              },
            }
          })
          break

        case 'tool_call':
          setSessionsByBorrower(prev => {
            const session = prev[borrowerId] || EMPTY_SESSION
            const idx = session.steps.findIndex(step => step.agent === data.agent)
            const nextStep = {
              agent: data.agent,
              tool: data.tool,
              status: 'running',
              output: data.output,
              ts: data.ts,
            }
            const steps = idx >= 0
              ? session.steps.map((step, stepIdx) => stepIdx === idx ? nextStep : step)
              : [...session.steps, nextStep]

            return {
              ...prev,
              [borrowerId]: {
                ...session,
                steps,
              },
            }
          })
          break

        case 'tool_result':
          setSessionsByBorrower(prev => {
            const session = prev[borrowerId] || EMPTY_SESSION
            const idx = session.steps.findIndex(step => step.agent === data.agent)
            const nextStep = {
              agent: data.agent,
              tool: data.tool,
              status: data.status,
              output: data.output,
              data: data.data || {},
              ts: data.ts,
            }
            const steps = idx >= 0
              ? session.steps.map((step, stepIdx) => stepIdx === idx ? nextStep : step)
              : [...session.steps, nextStep]

            return {
              ...prev,
              [borrowerId]: {
                ...session,
                llmStatus: null,
                steps,
              },
            }
          })
          break

        case 'result':
          setResultsByBorrower(prev => ({
            ...prev,
            [borrowerId]: data.result,
          }))
          setSessionsByBorrower(prev => ({
            ...prev,
            [borrowerId]: {
              ...(prev[borrowerId] || EMPTY_SESSION),
              llmStatus: null,
              agenticMode: data.result.agentic_mode,
            },
          }))
          if (isMobile) setMobilePanel('result')
          setRunningBorrower(current => current === borrowerId ? null : current)
          eventSource.close()
          break

        case 'error':
          setSessionsByBorrower(prev => ({
            ...prev,
            [borrowerId]: {
              ...(prev[borrowerId] || EMPTY_SESSION),
              llmStatus: null,
            },
          }))
          setRunningBorrower(current => current === borrowerId ? null : current)
          eventSource.close()
          break
      }
    }

    eventSource.onerror = () => {
      setSessionsByBorrower(prev => ({
        ...prev,
        [borrowerId]: {
          ...(prev[borrowerId] || EMPTY_SESSION),
          llmStatus: null,
        },
      }))
      setRunningBorrower(current => current === borrowerId ? null : current)
      eventSource.close()
    }
  }

  const handleDeleteBorrower = (borrowerId) => {
    if (selectedBorrower === borrowerId) {
      setSelectedBorrower(null)
      setSelectedProfile(null)
      if (isMobile) setMobilePanel('borrowers')
    }

    setResultsByBorrower(prev => {
      const next = { ...prev }
      delete next[borrowerId]
      return next
    })
    setSessionsByBorrower(prev => {
      const next = { ...prev }
      delete next[borrowerId]
      return next
    })
    setRunningBorrower(current => current === borrowerId ? null : current)
  }

  const mobileTabs = [
    { id: 'borrowers', label: 'Borrowers', enabled: true },
    { id: 'workflow', label: 'Workflow', enabled: Boolean(selectedBorrower) },
    { id: 'result', label: 'Result', enabled: Boolean(currentResult) },
  ]

  if (isMobile) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        background: 'var(--bg-primary)',
      }}>
        <div style={{
          position: 'sticky',
          top: 0,
          zIndex: 10,
          background: 'rgba(10,14,26,0.96)',
          backdropFilter: 'blur(14px)',
          borderBottom: '1px solid var(--border)',
          padding: '14px 14px 12px',
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: 12,
            marginBottom: 12,
          }}>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, letterSpacing: '1.5px', color: 'var(--accent-blue)' }}>
                CREDITAGENT
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                Mobile assessment workspace
              </div>
            </div>
            {selectedBorrower && (
              <div style={{
                padding: '6px 10px',
                borderRadius: 999,
                border: '1px solid rgba(59,130,246,0.25)',
                background: 'rgba(59,130,246,0.1)',
                color: '#93c5fd',
                fontSize: 10,
                letterSpacing: '1px',
              }}>
                {selectedBorrower.toUpperCase()}
              </div>
            )}
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
            gap: 8,
          }}>
            {mobileTabs.map(tab => {
              const active = mobilePanel === tab.id
              return (
                <button
                  key={tab.id}
                  type="button"
                  disabled={!tab.enabled}
                  onClick={() => tab.enabled && setMobilePanel(tab.id)}
                  style={{
                    border: `1px solid ${active ? 'rgba(59,130,246,0.35)' : 'var(--border)'}`,
                    background: active ? 'rgba(59,130,246,0.14)' : 'var(--bg-secondary)',
                    color: tab.enabled ? (active ? '#bfdbfe' : '#94a3b8') : '#475569',
                    borderRadius: 12,
                    padding: '10px 8px',
                    fontSize: 11,
                    fontWeight: 700,
                    letterSpacing: '0.8px',
                  }}
                >
                  {tab.label.toUpperCase()}
                </button>
              )
            })}
          </div>
        </div>

        <div style={{ flex: 1, minHeight: 0 }}>
          {mobilePanel === 'borrowers' && (
            <LeftSidebar
              selected={selectedBorrower}
              onSelect={setSelectedBorrower}
              onRun={handleRun}
              onDeleteBorrower={handleDeleteBorrower}
              isRunning={isRunning}
              runningBorrower={runningBorrower}
              resultsByBorrower={resultsByBorrower}
              isMobile
            />
          )}
          {mobilePanel === 'workflow' && (
            <AgentFlow
              borrower={selectedProfile}
              steps={currentSession.steps}
              thoughts={currentSession.thoughts}
              llmStatus={currentSession.llmStatus}
              isRunning={runningBorrower === selectedBorrower}
              agenticMode={currentSession.agenticMode}
              isMobile
            />
          )}
          {mobilePanel === 'result' && currentResult && (
            <ResultSidebar result={currentResult} borrowerId={selectedBorrower} isMobile />
          )}
        </div>
      </div>
    )
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: currentResult ? '280px 1fr 380px' : '280px 1fr',
      height: '100vh',
      transition: 'grid-template-columns 0.5s ease',
      gap: '1px',
      background: 'var(--border)',
    }}>
      <LeftSidebar
        selected={selectedBorrower}
        onSelect={setSelectedBorrower}
        onRun={handleRun}
        onDeleteBorrower={handleDeleteBorrower}
        isRunning={isRunning}
        runningBorrower={runningBorrower}
        resultsByBorrower={resultsByBorrower}
        isMobile={false}
      />
      <AgentFlow
        borrower={selectedProfile}
        steps={currentSession.steps}
        thoughts={currentSession.thoughts}
        llmStatus={currentSession.llmStatus}
        isRunning={runningBorrower === selectedBorrower}
        agenticMode={currentSession.agenticMode}
        isMobile={false}
      />
      {currentResult && (
        <ResultSidebar result={currentResult} borrowerId={selectedBorrower} isMobile={false} />
      )}
    </div>
  )
}
