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

  const currentSession = useMemo(
    () => (selectedBorrower && sessionsByBorrower[selectedBorrower]) || EMPTY_SESSION,
    [selectedBorrower, sessionsByBorrower]
  )
  const currentResult = selectedBorrower ? resultsByBorrower[selectedBorrower] || null : null
  const isRunning = runningBorrower !== null

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
        isRunning={isRunning}
        runningBorrower={runningBorrower}
        resultsByBorrower={resultsByBorrower}
      />
      <AgentFlow
        borrower={selectedProfile}
        steps={currentSession.steps}
        thoughts={currentSession.thoughts}
        llmStatus={currentSession.llmStatus}
        isRunning={runningBorrower === selectedBorrower}
        agenticMode={currentSession.agenticMode}
      />
      {currentResult && (
        <ResultSidebar result={currentResult} borrowerId={selectedBorrower} />
      )}
    </div>
  )
}
