import { useEffect, useRef } from 'react'

const STATUS_COLOR = {
  running: '#3b82f6',
  done: '#10b981',
  override: '#f59e0b',
  error: '#ef4444',
  thought: '#a855f7',
  thinking: '#8b5cf6',
}

export default function LiveLog({ steps }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [steps])

  if (steps.length === 0) return null

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      borderRadius: '12px',
      border: '1px solid var(--border)',
      padding: '16px',
      maxHeight: '300px',
      overflowY: 'auto',
      fontFamily: 'monospace',
    }}>
      <div style={{ fontSize: '10px', color: 'var(--text-secondary)', letterSpacing: '1px', marginBottom: 10 }}>
        AGENT EXECUTION LOG
      </div>
      {steps.map((step, i) => {
        const isThought = step.type === 'thought';
        const isToolCall = step.type === 'tool_call';
        const isLLMStatus = step.type === 'llm_status';

        let statusText = step.status?.toUpperCase() || '';
        if (isThought) statusText = 'THOUGHT';
        if (isLLMStatus) statusText = 'LLM';
        if (isToolCall) statusText = 'ACTION';

        return (
          <div key={i} style={{
            display: 'flex', gap: '10px',
            padding: isThought ? '8px 0' : '4px 0',
            borderBottom: '1px solid rgba(30,45,74,0.5)',
            animation: 'slideIn 0.3s ease',
            opacity: isLLMStatus ? 0.7 : 1,
            background: isThought ? 'rgba(168,85,247,0.05)' : 'transparent',
            borderRadius: isThought ? '4px' : '0',
          }}>
            <span style={{ 
              color: STATUS_COLOR[step.status] || STATUS_COLOR[step.type] || '#64748b', 
              fontSize: '11px', minWidth: '60px', fontWeight: isThought ? 700 : 400 
            }}>
              {statusText}
            </span>
            <span style={{ color: isThought ? '#d8b4fe' : '#94a3b8', fontSize: '11px', minWidth: '180px' }}>
              {step.agent || (isThought ? 'ReActOrchestrator' : '')}
            </span>
            <span style={{ 
              color: isThought ? '#e2e8f0' : (isLLMStatus ? '#a78bfa' : '#64748b'), 
              fontSize: '11px', whiteSpace: 'pre-wrap', flex: 1
            }}>
              {isThought ? `"${step.content}"` : step.output}
            </span>
          </div>
        )
      })}
      <div ref={bottomRef} />
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-10px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}
