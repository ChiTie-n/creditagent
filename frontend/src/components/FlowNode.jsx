const STATUS_STYLES = {
  idle:     { border: '#1e2d4a', bg: '#151d35', glow: 'none',                    dot: '#334155' },
  running:  { border: '#3b82f6', bg: 'rgba(59,130,246,0.1)', glow: '0 0 20px rgba(59,130,246,0.4)', dot: '#3b82f6' },
  done:     { border: '#10b981', bg: 'rgba(16,185,129,0.08)', glow: '0 0 15px rgba(16,185,129,0.25)', dot: '#10b981' },
  override: { border: '#f59e0b', bg: 'rgba(245,158,11,0.08)', glow: '0 0 15px rgba(245,158,11,0.3)', dot: '#f59e0b' },
  error:    { border: '#ef4444', bg: 'rgba(239,68,68,0.1)',  glow: '0 0 15px rgba(239,68,68,0.3)',  dot: '#ef4444' },
}

const AGENT_ICONS = {
  DataCollectionAgent:   '⬡',
  FinancialScoringAgent: '◈',
  AlternativeDataAgent:  '◎',
  RiskDecisionAgent:     '◆',
  ExplainabilityAgent:   '◉',
  BiasFairnessAgent:     '⬟',
  Orchestrator:          '⚙️',
  ReActOrchestrator:     '⚙️',
}

export default function FlowNode({ agent, step, isMobile = false }) {
  const status = step?.status || 'idle'
  const s = STATUS_STYLES[status] || STATUS_STYLES.idle

  // Clean up agent name for display
  const displayName = agent.replace('Agent', '').replace(/([A-Z])/g, ' $1').trim().toUpperCase()

  return (
    <div style={{
      border: `1px solid ${s.border}`,
      background: s.bg,
      boxShadow: s.glow,
      borderRadius: '12px',
      padding: isMobile ? '12px 14px' : '14px 18px',
      minWidth: isMobile ? '170px' : '200px',
      width: isMobile ? '170px' : 'auto',
      transition: 'all 0.4s ease',
      position: 'relative',
      flexShrink: 0,
    }}>
      {/* Status dot */}
      <div style={{
        position: 'absolute', top: 10, right: 10,
        width: 8, height: 8, borderRadius: '50%',
        background: s.dot,
        boxShadow: status === 'running' ? `0 0 8px ${s.dot}` : 'none',
        animation: status === 'running' ? 'pulse 1s infinite' : 'none',
      }} />

      <div style={{ fontSize: isMobile ? '18px' : '20px', marginBottom: 6 }}>
        {AGENT_ICONS[agent] || '◇'}
      </div>
      <div style={{ fontSize: isMobile ? '10px' : '11px', fontWeight: 700, letterSpacing: '1px', color: '#94a3b8' }}>
        {displayName}
      </div>

      {step?.output && (
        <div style={{
          fontSize: isMobile ? '9px' : '10px', color: '#64748b',
          marginTop: 6, lineHeight: 1.4,
          height: isMobile ? '26px' : '30px',
          overflow: 'hidden',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical'
        }}>
          {step.output}
        </div>
      )}

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}
