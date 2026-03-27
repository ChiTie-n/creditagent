const DECISION_STYLE = {
  APPROVE:  { color: '#10b981', glow: 'rgba(16,185,129,0.3)', bg: 'rgba(16,185,129,0.1)' },
  ESCALATE: { color: '#f59e0b', glow: 'rgba(245,158,11,0.3)',  bg: 'rgba(245,158,11,0.1)' },
  DENY:     { color: '#ef4444', glow: 'rgba(239,68,68,0.3)',   bg: 'rgba(239,68,68,0.1)' },
}

function ScoreBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: '11px', color: '#64748b' }}>{label}</span>
        <span style={{ fontSize: '11px', fontWeight: 700, color }}>{value}</span>
      </div>
      <div style={{ height: '4px', background: '#1e2d4a', borderRadius: '2px' }}>
        <div style={{
          height: '100%', width: `${(value / 1000) * 100}%`,
          background: color, borderRadius: '2px',
          transition: 'width 1s ease',
          boxShadow: `0 0 8px ${color}`,
        }} />
      </div>
    </div>
  )
}

export default function ResultSidebar({ result, borrowerId, isMobile = false }) {
  const ds = DECISION_STYLE[result.decision] || DECISION_STYLE.DENY
  const thinFileLabel = result.decision === 'APPROVE'
    ? '◆ THIN-FILE — Approved via Alternative Data'
    : '◆ THIN-FILE — Assessed via Alternative Data'

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      padding: isMobile ? '16px 14px 24px' : '24px 20px',
      overflowY: 'auto',
      borderLeft: isMobile ? 'none' : '1px solid var(--border)',
      borderTop: isMobile ? '1px solid var(--border)' : 'none',
      animation: 'slideInRight 0.5s ease',
      minHeight: 0,
    }}>
      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '1px', marginBottom: 16 }}>
        ASSESSMENT RESULT
      </div>
      {borrowerId && (
        <div style={{
          fontSize: '10px',
          color: '#60a5fa',
          letterSpacing: '1px',
          marginBottom: 12,
        }}>
          PROFILE: {borrowerId.toUpperCase()}
        </div>
      )}

      {/* Decision badge */}
      <div style={{
        textAlign: 'center', padding: '16px',
        borderRadius: '12px', marginBottom: '20px',
        border: `1px solid ${ds.color}`,
        background: ds.bg,
        boxShadow: `0 0 24px ${ds.glow}`,
      }}>
        <div style={{ fontSize: isMobile ? '24px' : '28px', fontWeight: 800, letterSpacing: isMobile ? '2px' : '3px', color: ds.color }}>
          {result.decision}
        </div>
        <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: 4 }}>
          {result.risk_tier}
        </div>
      </div>

      {/* Composite score */}
      <div style={{
        textAlign: 'center', marginBottom: '20px',
        padding: '16px', borderRadius: '10px',
        background: 'var(--bg-card)', border: '1px solid var(--border)',
      }}>
        <div style={{
          fontSize: isMobile ? '42px' : '52px', fontWeight: 800, lineHeight: 1,
          background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
        }}>
          {result.composite_score}
        </div>
        <div style={{ fontSize: '11px', color: '#64748b', marginTop: 4 }}>COMPOSITE SCORE</div>
      </div>

      {/* Score bars */}
      <ScoreBar label="Financial Score" value={result.financial_score} color="#3b82f6" />
      <ScoreBar label="Alternative Score" value={result.alternative_score} color="#8b5cf6" />

      {/* Credit terms */}
      {result.decision === 'APPROVE' && (
        <div style={{
          padding: '12px', borderRadius: '10px',
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.2)',
          marginBottom: '16px',
        }}>
          <div style={{ fontSize: '11px', color: '#10b981', marginBottom: 6 }}>CREDIT TERMS</div>
          <div style={{ fontSize: '13px', fontWeight: 600 }}>
            {(result.credit_limit / 1_000_000).toFixed(0)}M VND
          </div>
          <div style={{ fontSize: '11px', color: '#64748b' }}>{result.interest_rate_range}</div>
        </div>
      )}

      {/* Thin-file badge */}
      {result.is_underbanked && (
        <div style={{
          padding: '10px 12px', borderRadius: '8px', marginBottom: '16px',
          background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.3)',
          fontSize: '11px', color: '#a78bfa',
        }}>
          {thinFileLabel}
        </div>
      )}
      <div style={{ height: '1px', background: 'var(--border)', margin: '16px 0' }} />

      {/* Key strengths */}
      <div style={{ fontSize: '11px', color: '#10b981', letterSpacing: '1px', marginBottom: 8 }}>
        KEY STRENGTHS
      </div>
      {result.key_strengths?.map((s, i) => (
        <div key={i} style={{ fontSize: '12px', color: '#94a3b8', padding: '4px 0', borderBottom: '1px solid rgba(30,45,74,0.5)' }}>
          + {s}
        </div>
      ))}

      <div style={{ height: '1px', background: 'var(--border)', margin: '16px 0' }} />

      {/* Key concerns */}
      <div style={{ fontSize: '11px', color: '#ef4444', letterSpacing: '1px', marginBottom: 8 }}>
        KEY CONCERNS
      </div>
      {result.key_concerns?.map((c, i) => (
        <div key={i} style={{ fontSize: '12px', color: '#94a3b8', padding: '4px 0', borderBottom: '1px solid rgba(30,45,74,0.5)' }}>
          − {c}
        </div>
      ))}

      {/* Fairness */}
      <div style={{ height: '1px', background: 'var(--border)', margin: '16px 0' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '11px', color: '#64748b' }}>BIAS CHECK</span>
        <span style={{
          fontSize: '11px', fontWeight: 700,
          color: result.bias_detected ? '#ef4444' : '#10b981'
        }}>
          {result.bias_detected ? '✗ FAIL' : '✓ PASS'}
        </span>
      </div>

      <div style={{ height: '1px', background: 'var(--border)', margin: '16px 0' }} />

      {/* Report */}
      <div style={{ fontSize: '11px', color: '#64748b', letterSpacing: '1px', marginBottom: 8 }}>
        AI REPORT
      </div>
      <div style={{ fontSize: '11px', color: '#94a3b8', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>
        {result.report}
      </div>

      <style>{`
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(40px); }
          to { opacity: 1; transform: translateX(0); }
        }
      `}</style>
    </div>
  )
}
