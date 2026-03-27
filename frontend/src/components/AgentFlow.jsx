import { useEffect, useRef } from 'react'
import FlowNode from './FlowNode'

const AGENT_ORDER = [
  'DataCollectionAgent',
  'FinancialScoringAgent',
  'AlternativeDataAgent',
  'RiskDecisionAgent',
  'ExplainabilityAgent',
  'BiasFairnessAgent',
]

function formatCurrency(value) {
  if (!value) return 'N/A'
  if (value >= 1_000_000_000) return `${(value / 1_000_000_000).toFixed(1)}B VND`
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(0)}M VND`
  return `${Math.round(value).toLocaleString()} VND`
}

function initials(name) {
  return (name || 'NA')
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map(part => part[0]?.toUpperCase() || '')
    .join('')
}

function Connector({ active }) {
  return (
    <div style={{
      width: '36px',
      height: '2px',
      background: active
        ? 'linear-gradient(90deg, #3b82f6, #8b5cf6)'
        : '#1e2d4a',
      alignSelf: 'center',
      flexShrink: 0,
      transition: 'background 0.5s ease',
      boxShadow: active ? '0 0 8px rgba(59,130,246,0.5)' : 'none',
    }} />
  )
}

function ThinkingBubble({ llmStatus }) {
  if (!llmStatus) return null
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '8px',
      padding: '8px 14px',
      background: 'rgba(59,130,246,0.08)',
      border: '1px solid rgba(59,130,246,0.2)',
      borderRadius: '8px',
      animation: 'fadeIn 0.3s ease',
    }}>
      <div style={{ display: 'flex', gap: '3px', alignItems: 'center' }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: '5px',
            height: '5px',
            borderRadius: '50%',
            background: '#3b82f6',
            animation: `bounce 1s ${i * 0.2}s infinite`,
          }} />
        ))}
      </div>
      <span style={{ fontSize: '12px', color: '#60a5fa' }}>
        LLM reasoning...
      </span>
      <style>{`
        @keyframes bounce {
          0%, 100% { transform: translateY(0); opacity: 0.4; }
          50% { transform: translateY(-4px); opacity: 1; }
        }
      `}</style>
    </div>
  )
}

function ThoughtBubble({ thought }) {
  return (
    <div style={{
      padding: '10px 14px',
      background: 'rgba(139,92,246,0.08)',
      border: '1px solid rgba(139,92,246,0.2)',
      borderLeft: '3px solid #8b5cf6',
      borderRadius: '0 8px 8px 0',
      animation: 'slideIn 0.3s ease',
    }}>
      <div style={{ fontSize: '10px', color: '#8b5cf6', letterSpacing: '1px', marginBottom: 4 }}>
        LLM THOUGHT
      </div>
      <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.5 }}>
        {thought.content}
      </div>
    </div>
  )
}

function AgenticBadge({ mode, isRunning }) {
  if (isRunning) {
    return (
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: '6px',
        padding: '4px 10px',
        background: 'rgba(59,130,246,0.1)',
        border: '1px solid rgba(59,130,246,0.3)',
        borderRadius: '20px',
        fontSize: '11px', color: '#60a5fa',
      }}>
        <div style={{
          width: '6px', height: '6px', borderRadius: '50%',
          background: '#3b82f6',
          animation: 'pulse 1s infinite',
        }} />
        REACT LOOP ACTIVE
      </div>
    )
  }
  if (mode === 'react_llm') {
    return (
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: '6px',
        padding: '4px 10px',
        background: 'rgba(16,185,129,0.1)',
        border: '1px solid rgba(16,185,129,0.2)',
        borderRadius: '20px',
        fontSize: '11px', color: '#34d399',
      }}>
        AGENTIC - LLM DRIVEN
      </div>
    )
  }
  if (mode === 'fallback_pipeline') {
    return (
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: '6px',
        padding: '4px 10px',
        background: 'rgba(245,158,11,0.1)',
        border: '1px solid rgba(245,158,11,0.2)',
        borderRadius: '20px',
        fontSize: '11px', color: '#fbbf24',
      }}>
        DETERMINISTIC FALLBACK
      </div>
    )
  }
  return null
}

function SourceBadge({ label, active, color }) {
  return (
    <div style={{
      padding: '4px 8px',
      borderRadius: '999px',
      border: `1px solid ${active ? color : 'rgba(100,116,139,0.25)'}`,
      background: active ? `${color}18` : 'rgba(21,29,53,0.8)',
      color: active ? color : '#64748b',
      fontSize: '10px',
      letterSpacing: '0.8px',
    }}>
      {label}
    </div>
  )
}

function BorrowerCard({ borrower, isMobile = false }) {
  if (!borrower) return null

  const profile = borrower.profile || {}
  const sources = borrower.sources_available || {}
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: isMobile ? '1fr' : '120px 1fr',
      gap: isMobile ? '16px' : '18px',
      padding: isMobile ? '16px' : '18px 20px',
      borderRadius: '18px',
      border: '1px solid rgba(30,45,74,0.9)',
      background: 'linear-gradient(135deg, rgba(17,24,39,0.92), rgba(10,14,26,0.96))',
      boxShadow: '0 18px 60px rgba(2,6,23,0.35)',
    }}>
      <div style={{ display: 'flex', flexDirection: isMobile ? 'row' : 'column', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: isMobile ? 68 : 84,
          height: isMobile ? 68 : 84,
          borderRadius: '24px',
          display: 'grid',
          placeItems: 'center',
          background: 'linear-gradient(135deg, rgba(59,130,246,0.28), rgba(16,185,129,0.18))',
          border: '1px solid rgba(96,165,250,0.28)',
          color: '#dbeafe',
          fontSize: isMobile ? '22px' : '28px',
          fontWeight: 800,
          letterSpacing: '1px',
        }}>
          {initials(borrower.name)}
        </div>
        <div style={{
          fontSize: '10px',
          color: '#60a5fa',
          letterSpacing: '1.2px',
          border: '1px solid rgba(59,130,246,0.25)',
          borderRadius: '999px',
          padding: '4px 8px',
        }}>
          {borrower.borrower_id.toUpperCase()}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'flex-start', flexDirection: isMobile ? 'column' : 'row' }}>
          <div>
            <div style={{ fontSize: '11px', color: '#64748b', letterSpacing: '1.5px', marginBottom: 6 }}>
              CUSTOMER PROFILE
            </div>
            <div style={{ fontSize: isMobile ? '20px' : '24px', fontWeight: 700, color: '#f8fafc', lineHeight: 1.1 }}>
              {borrower.name}
            </div>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: 6 }}>
              {borrower.business_name}
            </div>
          </div>
          <div style={{
            minWidth: isMobile ? 'auto' : 160,
            width: isMobile ? '100%' : 'auto',
            textAlign: isMobile ? 'left' : 'right',
            padding: '10px 12px',
            borderRadius: '12px',
            background: 'rgba(16,185,129,0.08)',
            border: '1px solid rgba(16,185,129,0.18)',
          }}>
            <div style={{ fontSize: '10px', color: '#34d399', letterSpacing: '1px' }}>
              REQUESTED LOAN
            </div>
            <div style={{ fontSize: isMobile ? '18px' : '20px', fontWeight: 700, color: '#ecfeff', marginTop: 4 }}>
              {formatCurrency(borrower.loan_amount_requested)}
            </div>
          </div>
        </div>

        <div style={{ fontSize: '12px', color: '#94a3b8', lineHeight: 1.6 }}>
          {borrower.scenario}
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: isMobile ? 'repeat(2, minmax(0, 1fr))' : 'repeat(4, minmax(0, 1fr))', gap: 10 }}>
          <InfoStat label="Business Type" value={borrower.business_type} />
          <InfoStat label="Loan Purpose" value={borrower.loan_purpose} />
          <InfoStat label="Region" value={profile.region || 'N/A'} />
          <InfoStat label="Province" value={profile.province || 'N/A'} />
        </div>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          <SourceBadge label="BANK DATA" active={sources.bank_data} color="#60a5fa" />
          <SourceBadge label="UTILITY" active={sources.utility_data} color="#34d399" />
          <SourceBadge label="MOBILE" active={sources.mobile_data} color="#a78bfa" />
          {!borrower.has_bank_data && (
            <SourceBadge label="THIN-FILE" active color="#f59e0b" />
          )}
        </div>
      </div>
    </div>
  )
}

function InfoStat({ label, value }) {
  return (
    <div style={{
      padding: '10px 12px',
      borderRadius: '12px',
      background: 'rgba(21,29,53,0.85)',
      border: '1px solid rgba(30,45,74,0.85)',
      minHeight: 72,
    }}>
      <div style={{ fontSize: '10px', color: '#64748b', letterSpacing: '1px', marginBottom: 6 }}>
        {label}
      </div>
      <div style={{
        fontSize: '13px',
        color: '#e2e8f0',
        lineHeight: 1.45,
        display: '-webkit-box',
        overflow: 'hidden',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
      }}>
        {value || 'N/A'}
      </div>
    </div>
  )
}

export default function AgentFlow({ borrower, steps, thoughts, llmStatus, isRunning, agenticMode, isMobile = false }) {
  const logRef = useRef(null)
  const getStep = (agent) => steps.find(s => s.agent === agent)

  useEffect(() => {
    logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: 'smooth' })
  }, [thoughts, steps])

  const isConnectorActive = (fromAgent) => {
    const fromStep = getStep(fromAgent)
    return fromStep?.status === 'done' || fromStep?.status === 'override'
  }

  return (
    <div style={{
      background: 'var(--bg-primary)',
      display: 'flex',
      flexDirection: 'column',
      padding: isMobile ? '16px 14px 24px' : '28px 32px',
      gap: isMobile ? '18px' : '24px',
      overflow: 'hidden',
      minHeight: 0,
    }}>
      {borrower && <BorrowerCard borrower={borrower} isMobile={isMobile} />}

      <div style={{ display: 'flex', alignItems: isMobile ? 'flex-start' : 'center', gap: '16px', flexDirection: isMobile ? 'column' : 'row' }}>
        <div>
          <div style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '2px' }}>
            AGENTIC WORKFLOW
          </div>
        </div>
        <AgenticBadge mode={agenticMode} isRunning={isRunning} />
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        flexWrap: isMobile ? 'nowrap' : 'wrap',
        rowGap: '16px',
        columnGap: isMobile ? '0' : '0',
        overflowX: isMobile ? 'auto' : 'visible',
        overflowY: 'hidden',
        paddingBottom: isMobile ? 6 : 0,
      }}>
        {AGENT_ORDER.map((agent, i) => (
          <div key={agent} style={{ display: 'flex', alignItems: 'center' }}>
            <FlowNode agent={agent} step={getStep(agent)} isMobile={isMobile} />
            {i < AGENT_ORDER.length - 1 && (
              <Connector active={isConnectorActive(agent)} />
            )}
          </div>
        ))}
      </div>

      <div
        ref={logRef}
        style={{
          flex: 1,
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px',
          minHeight: 0,
        }}
      >
        {[
          ...thoughts.map(t => ({ ...t, _type: 'thought' })),
          ...steps.filter(s => s.status === 'done' || s.status === 'error' || s.status === 'override')
            .map(s => ({ ...s, _type: 'step' })),
        ]
          .sort((a, b) => (a.ts || 0) - (b.ts || 0))
          .map((item, i) => (
            item._type === 'thought'
              ? <ThoughtBubble key={`t-${i}`} thought={item} />
              : <StepLog key={`s-${i}`} step={item} isMobile={isMobile} />
          ))}

        <ThinkingBubble llmStatus={llmStatus} />
      </div>

      <style>{`
        @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }
        @keyframes slideIn {
          from { opacity: 0; transform: translateX(-8px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.3; }
        }
      `}</style>
    </div>
  )
}

function StepLog({ step, isMobile = false }) {
  const STATUS_COLOR = { done: '#10b981', error: '#ef4444', override: '#f59e0b' }
  const color = STATUS_COLOR[step.status] || '#64748b'

  return (
    <div style={{
      display: 'flex', gap: '10px', alignItems: 'flex-start',
      flexDirection: isMobile ? 'column' : 'row',
      padding: '6px 10px',
      background: 'var(--bg-secondary)',
      borderRadius: '6px',
      borderLeft: `2px solid ${color}`,
      animation: 'slideIn 0.3s ease',
      fontSize: '12px',
    }}>
      <span style={{ color, minWidth: isMobile ? 'auto' : '40px', fontWeight: 600, fontSize: '10px', paddingTop: 1 }}>
        {step.status?.toUpperCase()}
      </span>
      <span style={{ color: '#94a3b8', minWidth: isMobile ? 'auto' : '150px' }}>
        {step.agent?.replace('Agent', ' Agent')}
      </span>
      <span style={{ color: '#64748b', lineHeight: 1.4 }}>
        {step.output}
      </span>
    </div>
  )
}
