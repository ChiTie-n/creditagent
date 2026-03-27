import { useEffect, useState } from 'react'

const initialForm = {
  name: '',
  business_name: '',
  business_type: 'household_business',
  scenario: '',
  loan_purpose: '',
  loan_amount_requested: '20000000',
  gender: 'female',
  age_group: '25-35',
  employment_type: 'household_business',
  region: 'urban',
  province: 'Ho Chi Minh City',
  utility_provider: 'EVN',
  utility_months_history: '24',
  utility_on_time_rate: '0.95',
  mobile_platform: 'MoMo',
  mobile_consistency_score: '0.85',
  mobile_monthly_volume: '15000000',
  has_bank_data: false,
  bank_limit_bal: '30000000',
  bank_sex: '2',
  bank_education: '2',
  bank_marriage: '1',
  bank_age: '30',
  bank_pay_0: '0',
  bank_pay_2: '0',
  bank_pay_3: '0',
  bank_bill_amt1: '10000000',
  bank_pay_amt1: '5000000',
}

const inputStyle = {
  width: '100%',
  background: 'var(--bg-card)',
  border: '1px solid var(--border)',
  color: 'var(--text-primary)',
  borderRadius: '8px',
  padding: '9px 10px',
  fontSize: '12px',
  outline: 'none',
}

const labelStyle = {
  fontSize: '10px',
  color: 'var(--text-secondary)',
  letterSpacing: '0.8px',
  marginBottom: 6,
}

function Field({ label, children }) {
  return (
    <label style={{ display: 'block' }}>
      <div style={labelStyle}>{label}</div>
      {children}
    </label>
  )
}

export default function LeftSidebar({
  selected,
  onSelect,
  onRun,
  onDeleteBorrower,
  isRunning,
  runningBorrower,
  resultsByBorrower,
  isMobile = false,
}) {
  const [personas, setPersonas] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [formError, setFormError] = useState('')
  const [form, setForm] = useState(initialForm)

  useEffect(() => {
    fetch('/personas')
      .then(r => r.json())
      .then(setPersonas)
      .catch(() => {})
  }, [])

  const selectedHasResult = selected ? Boolean(resultsByBorrower[selected]) : false
  const formGrid = isMobile ? '1fr' : '1fr 1fr'

  const updateForm = (key, value) => {
    setForm(prev => ({ ...prev, [key]: value }))
  }

  const resetForm = () => {
    setForm(initialForm)
    setFormError('')
  }

  const handleCreatePersona = async () => {
    setFormError('')

    if (!form.name.trim() || !form.scenario.trim() || !form.business_name.trim()) {
      setFormError('Name, business name, and scenario are required.')
      return
    }

    const payload = {
      name: form.name.trim(),
      business_name: form.business_name.trim(),
      business_type: form.business_type.trim(),
      scenario: form.scenario.trim(),
      loan_purpose: form.loan_purpose.trim() || 'Working capital',
      loan_amount_requested: Number(form.loan_amount_requested),
      expected_decision: 'UNKNOWN',
      profile: {
        gender: form.gender,
        age_group: form.age_group,
        employment_type: form.employment_type.trim(),
        region: form.region,
        province: form.province.trim(),
      },
      utility_data: {
        provider: form.utility_provider.trim(),
        months_history: Number(form.utility_months_history),
        on_time_rate: Number(form.utility_on_time_rate),
      },
      mobile_data: {
        platform: form.mobile_platform.trim(),
        consistency_score: Number(form.mobile_consistency_score),
        monthly_volume: Number(form.mobile_monthly_volume),
      },
      bank_data: form.has_bank_data ? {
        LIMIT_BAL: Number(form.bank_limit_bal),
        SEX: Number(form.bank_sex),
        EDUCATION: Number(form.bank_education),
        MARRIAGE: Number(form.bank_marriage),
        AGE: Number(form.bank_age),
        PAY_0: Number(form.bank_pay_0),
        PAY_2: Number(form.bank_pay_2),
        PAY_3: Number(form.bank_pay_3),
        BILL_AMT1: Number(form.bank_bill_amt1),
        PAY_AMT1: Number(form.bank_pay_amt1),
      } : null,
    }

    setIsSaving(true)
    try {
      const response = await fetch('/personas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      const data = await response.json()
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map(item => item.msg).join(', ')
          : data.detail
        throw new Error(detail || 'Failed to create borrower')
      }

      setPersonas(prev => [...prev, data])
      onSelect(data.borrower_id)
      setShowForm(false)
      resetForm()
    } catch (error) {
      setFormError(error.message || 'Failed to create borrower')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeletePersona = async (borrowerId, name) => {
    const confirmed = window.confirm(`Delete custom profile "${name}"?`)
    if (!confirmed) return

    try {
      const response = await fetch(`/personas/${borrowerId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        let detail = 'Failed to delete borrower'
        try {
          const data = await response.json()
          detail = data.detail || detail
        } catch {}
        throw new Error(detail)
      }

      setPersonas(prev => prev.filter(persona => persona.borrower_id !== borrowerId))
      onDeleteBorrower?.(borrowerId)
    } catch (error) {
      window.alert(error.message || 'Failed to delete borrower')
    }
  }

  return (
    <div style={{
      background: 'var(--bg-secondary)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      minHeight: 0,
    }}>
      <div style={{
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        padding: isMobile ? '16px 14px 16px' : '24px 20px 18px',
        display: 'flex',
        flexDirection: 'column',
        gap: '20px',
        WebkitOverflowScrolling: 'touch',
        overscrollBehavior: 'contain',
      }}>
      {!isMobile && (
        <div>
        <div style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '2px', color: 'var(--accent-blue)' }}>
          CREDITAGENT
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: 4 }}>
          AGENTIC AI CREDIT SYSTEM
        </div>
        </div>
      )}

      {!isMobile && <div style={{ height: '1px', background: 'var(--border)' }} />}

      <div style={{
        border: '1px solid var(--border)',
        borderRadius: '12px',
        background: 'rgba(59,130,246,0.05)',
        padding: '12px',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: showForm ? 12 : 0 }}>
          <div>
            <div style={{ fontSize: '11px', color: '#93c5fd', letterSpacing: '1px' }}>BORROWER MANAGEMENT</div>
            <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: 4 }}>
              Add a custom profile for ad-hoc assessment
            </div>
          </div>
          <button
            onClick={() => {
              setShowForm(prev => !prev)
              setFormError('')
            }}
            style={{
              border: '1px solid rgba(59,130,246,0.35)',
              background: showForm ? 'rgba(59,130,246,0.15)' : 'rgba(59,130,246,0.08)',
              color: '#93c5fd',
              borderRadius: '999px',
              padding: '6px 10px',
              fontSize: '10px',
              letterSpacing: '1px',
              cursor: 'pointer',
            }}
          >
            {showForm ? 'CLOSE' : 'ADD'}
          </button>
        </div>

        {showForm && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            <Field label="BORROWER NAME">
              <input value={form.name} onChange={e => updateForm('name', e.target.value)} style={inputStyle} />
            </Field>
            <Field label="BUSINESS NAME">
              <input value={form.business_name} onChange={e => updateForm('business_name', e.target.value)} style={inputStyle} />
            </Field>
            <Field label="SCENARIO">
              <textarea
                value={form.scenario}
                onChange={e => updateForm('scenario', e.target.value)}
                style={{ ...inputStyle, minHeight: 64, resize: 'vertical' }}
              />
            </Field>
            <Field label="LOAN PURPOSE">
              <input value={form.loan_purpose} onChange={e => updateForm('loan_purpose', e.target.value)} style={inputStyle} />
            </Field>

            <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
              <Field label="LOAN AMOUNT">
                <input value={form.loan_amount_requested} onChange={e => updateForm('loan_amount_requested', e.target.value)} style={inputStyle} />
              </Field>
              <Field label="BUSINESS TYPE">
                <input value={form.business_type} onChange={e => updateForm('business_type', e.target.value)} style={inputStyle} />
              </Field>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
              <Field label="GENDER">
                <select value={form.gender} onChange={e => updateForm('gender', e.target.value)} style={inputStyle}>
                  <option value="female">Female</option>
                  <option value="male">Male</option>
                </select>
              </Field>
              <Field label="AGE GROUP">
                <select value={form.age_group} onChange={e => updateForm('age_group', e.target.value)} style={inputStyle}>
                  <option value="18-25">18-25</option>
                  <option value="25-35">25-35</option>
                  <option value="35-45">35-45</option>
                  <option value="45-55">45-55</option>
                </select>
              </Field>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
              <Field label="EMPLOYMENT TYPE">
                <input value={form.employment_type} onChange={e => updateForm('employment_type', e.target.value)} style={inputStyle} />
              </Field>
              <Field label="REGION">
                <select value={form.region} onChange={e => updateForm('region', e.target.value)} style={inputStyle}>
                  <option value="urban">Urban</option>
                  <option value="suburban">Suburban</option>
                  <option value="rural">Rural</option>
                </select>
              </Field>
            </div>

            <Field label="PROVINCE">
              <input value={form.province} onChange={e => updateForm('province', e.target.value)} style={inputStyle} />
            </Field>

            <div style={{
              marginTop: 4,
              paddingTop: 10,
              borderTop: '1px solid rgba(30,45,74,0.8)',
              display: 'flex',
              flexDirection: 'column',
              gap: 10,
            }}>
              <div style={{ fontSize: '10px', color: '#34d399', letterSpacing: '1px' }}>ALTERNATIVE DATA</div>
              <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                <Field label="UTILITY PROVIDER">
                  <input value={form.utility_provider} onChange={e => updateForm('utility_provider', e.target.value)} style={inputStyle} />
                </Field>
                <Field label="MOBILE PLATFORM">
                  <input value={form.mobile_platform} onChange={e => updateForm('mobile_platform', e.target.value)} style={inputStyle} />
                </Field>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                <Field label="UTILITY MONTHS">
                  <input value={form.utility_months_history} onChange={e => updateForm('utility_months_history', e.target.value)} style={inputStyle} />
                </Field>
                <Field label="ON-TIME RATE">
                  <input value={form.utility_on_time_rate} onChange={e => updateForm('utility_on_time_rate', e.target.value)} style={inputStyle} />
                </Field>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                <Field label="CONSISTENCY SCORE">
                  <input value={form.mobile_consistency_score} onChange={e => updateForm('mobile_consistency_score', e.target.value)} style={inputStyle} />
                </Field>
                <Field label="MONTHLY VOLUME">
                  <input value={form.mobile_monthly_volume} onChange={e => updateForm('mobile_monthly_volume', e.target.value)} style={inputStyle} />
                </Field>
              </div>
            </div>

            <div style={{
              marginTop: 4,
              paddingTop: 10,
              borderTop: '1px solid rgba(30,45,74,0.8)',
            }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: '11px', color: '#cbd5e1', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={form.has_bank_data}
                  onChange={e => updateForm('has_bank_data', e.target.checked)}
                />
                Include bank data
              </label>
            </div>

            {form.has_bank_data && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <div style={{ fontSize: '10px', color: '#fbbf24', letterSpacing: '1px' }}>BANK DATA</div>
                <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                  <Field label="LIMIT BAL">
                    <input value={form.bank_limit_bal} onChange={e => updateForm('bank_limit_bal', e.target.value)} style={inputStyle} />
                  </Field>
                  <Field label="AGE">
                    <input value={form.bank_age} onChange={e => updateForm('bank_age', e.target.value)} style={inputStyle} />
                  </Field>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                  <Field label="SEX">
                    <select value={form.bank_sex} onChange={e => updateForm('bank_sex', e.target.value)} style={inputStyle}>
                      <option value="1">Male</option>
                      <option value="2">Female</option>
                    </select>
                  </Field>
                  <Field label="EDUCATION">
                    <select value={form.bank_education} onChange={e => updateForm('bank_education', e.target.value)} style={inputStyle}>
                      <option value="1">Graduate</option>
                      <option value="2">University</option>
                      <option value="3">High School</option>
                      <option value="4">Other</option>
                    </select>
                  </Field>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                  <Field label="MARRIAGE">
                    <select value={form.bank_marriage} onChange={e => updateForm('bank_marriage', e.target.value)} style={inputStyle}>
                      <option value="1">Married</option>
                      <option value="2">Single</option>
                      <option value="3">Other</option>
                    </select>
                  </Field>
                  <Field label="PAY 0">
                    <input value={form.bank_pay_0} onChange={e => updateForm('bank_pay_0', e.target.value)} style={inputStyle} />
                  </Field>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                  <Field label="PAY 2">
                    <input value={form.bank_pay_2} onChange={e => updateForm('bank_pay_2', e.target.value)} style={inputStyle} />
                  </Field>
                  <Field label="PAY 3">
                    <input value={form.bank_pay_3} onChange={e => updateForm('bank_pay_3', e.target.value)} style={inputStyle} />
                  </Field>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: formGrid, gap: 10 }}>
                  <Field label="BILL AMT1">
                    <input value={form.bank_bill_amt1} onChange={e => updateForm('bank_bill_amt1', e.target.value)} style={inputStyle} />
                  </Field>
                  <Field label="PAY AMT1">
                    <input value={form.bank_pay_amt1} onChange={e => updateForm('bank_pay_amt1', e.target.value)} style={inputStyle} />
                  </Field>
                </div>
              </div>
            )}

            {formError && (
              <div style={{
                color: '#fca5a5',
                fontSize: '11px',
                lineHeight: 1.5,
                padding: '8px 10px',
                borderRadius: '8px',
                border: '1px solid rgba(239,68,68,0.3)',
                background: 'rgba(239,68,68,0.08)',
              }}>
                {formError}
              </div>
            )}

            <button
              onClick={handleCreatePersona}
              disabled={isSaving}
              style={{
                marginTop: 4,
                padding: '11px 12px',
                borderRadius: '10px',
                border: '1px solid rgba(16,185,129,0.25)',
                background: isSaving ? 'var(--bg-card)' : 'linear-gradient(135deg, rgba(16,185,129,0.18), rgba(59,130,246,0.18))',
                color: 'white',
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '1px',
                cursor: isSaving ? 'not-allowed' : 'pointer',
              }}
            >
              {isSaving ? 'SAVING...' : 'CREATE BORROWER'}
            </button>
          </div>
        )}
      </div>

      <div>
        <div style={{ fontSize: '11px', color: 'var(--text-secondary)', letterSpacing: '1px', marginBottom: 12 }}>
          SELECT BORROWER
        </div>
        {isMobile && selected && (
          <div style={{
            marginBottom: 12,
            padding: '10px 12px',
            borderRadius: '10px',
            border: '1px solid rgba(59,130,246,0.22)',
            background: 'rgba(59,130,246,0.08)',
            fontSize: '11px',
            color: '#bfdbfe',
            lineHeight: 1.5,
          }}>
            Profile selected. Tap <strong>RUN ASSESSMENT</strong> below to start reviewing this borrower.
          </div>
        )}
        {personas.map(p => {
          const hasResult = Boolean(resultsByBorrower[p.borrower_id])
          const isSelected = selected === p.borrower_id
          const isActiveRun = runningBorrower === p.borrower_id

          return (
            <div
              key={p.borrower_id}
              onClick={() => onSelect(p.borrower_id)}
              style={{
                padding: '12px 14px',
                borderRadius: '10px',
                marginBottom: '8px',
                cursor: 'pointer',
                border: `1px solid ${isSelected ? 'var(--accent-blue)' : 'var(--border)'}`,
                background: isSelected ? 'rgba(59,130,246,0.1)' : 'var(--bg-card)',
                transition: 'all 0.2s ease',
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', gap: 8, alignItems: 'flex-start' }}>
                <div style={{ fontSize: '13px', fontWeight: 600 }}>{p.name}</div>
                <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexShrink: 0 }}>
                  {hasResult && (
                    <div style={{
                      fontSize: '9px',
                      color: '#34d399',
                      letterSpacing: '0.8px',
                      border: '1px solid rgba(52,211,153,0.25)',
                      background: 'rgba(16,185,129,0.08)',
                      padding: '2px 6px',
                      borderRadius: '999px',
                    }}>
                      SAVED
                    </div>
                  )}
                  {p.borrower_id.startsWith('custom_') && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeletePersona(p.borrower_id, p.name)
                      }}
                      style={{
                        border: '1px solid rgba(239,68,68,0.28)',
                        background: 'rgba(239,68,68,0.08)',
                        color: '#fda4af',
                        borderRadius: '999px',
                        padding: '3px 8px',
                        fontSize: '9px',
                        letterSpacing: '0.8px',
                        cursor: 'pointer',
                      }}
                    >
                      DELETE
                    </button>
                  )}
                </div>
              </div>
              <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: 2 }}>{p.scenario}</div>
              <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginTop: 4, flexWrap: 'wrap' }}>
                {!p.has_bank_data && (
                  <div style={{
                    fontSize: '10px',
                    color: 'var(--accent-purple)',
                    letterSpacing: '0.5px',
                  }}>
                    ◆ THIN-FILE
                  </div>
                )}
                {p.borrower_id.startsWith('custom_') && (
                  <div style={{
                    fontSize: '10px',
                    color: '#fbbf24',
                    letterSpacing: '0.5px',
                  }}>
                    CUSTOM
                  </div>
                )}
                {isActiveRun && (
                  <div style={{
                    fontSize: '10px',
                    color: '#60a5fa',
                    letterSpacing: '0.5px',
                  }}>
                    RUNNING
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
      </div>

      <div style={{
        borderTop: '1px solid var(--border)',
        background: 'linear-gradient(180deg, rgba(15,22,41,0.92), rgba(15,22,41,1))',
        boxShadow: '0 -10px 24px rgba(2,6,23,0.22)',
        padding: isMobile ? '12px 14px calc(14px + env(safe-area-inset-bottom))' : '14px 20px 18px',
      }}>
        <button
          onClick={() => selected && onRun(selected)}
          disabled={!selected || isRunning}
          style={{
            padding: '14px',
            borderRadius: '10px',
            border: 'none',
            background: isRunning
              ? 'var(--bg-card)'
              : 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
            color: 'white',
            fontWeight: 700,
            fontSize: '13px',
            letterSpacing: '2px',
            cursor: selected && !isRunning ? 'pointer' : 'not-allowed',
            opacity: !selected ? 0.5 : 1,
            transition: 'all 0.2s ease',
            boxShadow: isRunning ? 'none' : '0 0 20px var(--glow-blue)',
            width: '100%',
          }}
        >
          {isRunning ? 'ASSESSING...' : selectedHasResult ? 'RE-RUN ASSESSMENT' : 'RUN ASSESSMENT'}
        </button>

        <div style={{ fontSize: '10px', color: 'var(--text-muted)', lineHeight: '1.8', marginTop: 10 }}>
          ReAct Loop · Tool Registry · XGBoost · SHAP · Fairness Metrics
        </div>
      </div>

      {false && !isMobile && <div style={{ flex: 1 }} />}

      <button
        onClick={() => selected && onRun(selected)}
        disabled={!selected || isRunning}
        style={{
          display: 'none',
          position: isMobile ? 'sticky' : 'static',
          bottom: isMobile ? 12 : 'auto',
          padding: '14px',
          borderRadius: '10px',
          border: 'none',
          background: isRunning
            ? 'var(--bg-card)'
            : 'linear-gradient(135deg, var(--accent-blue), var(--accent-purple))',
          color: 'white',
          fontWeight: 700,
          fontSize: '13px',
          letterSpacing: '2px',
          cursor: selected && !isRunning ? 'pointer' : 'not-allowed',
          opacity: !selected ? 0.5 : 1,
          transition: 'all 0.2s ease',
          boxShadow: isRunning ? 'none' : '0 0 20px var(--glow-blue)',
          width: '100%',
          marginTop: isMobile ? 'auto' : 0,
          zIndex: isMobile ? 1 : 'auto',
        }}
      >
        {isRunning ? '◌  ASSESSING...' : selectedHasResult ? '▶  RE-RUN ASSESSMENT' : '▶  RUN ASSESSMENT'}
      </button>

      <div style={{ display: 'none', fontSize: '10px', color: 'var(--text-muted)', lineHeight: '1.8' }}>
        ReAct Loop · Tool Registry · XGBoost · SHAP · Fairness Metrics
      </div>
    </div>
  )
}
