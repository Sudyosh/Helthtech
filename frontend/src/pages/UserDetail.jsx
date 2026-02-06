import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getUserDetail, getRiskAnalysis } from '../services/api'
import { th } from '../i18n/th'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import './UserDetail.css'

function UserDetail() {
    const { userId } = useParams()
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadUserDetail()
    }, [userId])

    const loadUserDetail = async () => {
        setLoading(true)
        try {
            const data = await getUserDetail(userId)
            setUser(data)
        } catch (error) {
            console.error('Error loading user:', error)
            // Mock data for demo
            setUser(getMockUserDetail())
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="user-detail-loading">
                <div className="loading-spinner"></div>
                <p>{th.userDetail.loading}</p>
            </div>
        )
    }

    if (!user) {
        return (
            <div className="user-detail-error">
                <p>{th.userDetail.notFound}</p>
                <Link to="/dashboard" className="btn btn-secondary">{th.userDetail.back}</Link>
            </div>
        )
    }

    return (
        <div className="user-detail">
            <header className="user-detail-header">
                <Link to="/dashboard" className="back-btn">{th.userDetail.back}</Link>
                <h1>{th.userDetail.title}: {user.user_id}</h1>
            </header>

            <div className="user-detail-content">
                <div className="detail-grid">
                    {/* User Info Card */}
                    <div className="card info-card">
                        <h3>{th.userDetail.userInfo.title}</h3>
                        <dl>
                            <dt>{th.userDetail.userInfo.id}:</dt>
                            <dd>{user.user_id}</dd>
                            <dt>{th.userDetail.userInfo.created}:</dt>
                            <dd>{new Date(user.created_at).toLocaleDateString('th-TH')}</dd>
                            <dt>ความยินยอม:</dt>
                            <dd>{user.consent ? '✅ ให้แล้ว' : '❌ ยังไม่ให้'}</dd>
                        </dl>
                    </div>

                    {/* Risk Summary */}
                    <div className="card risk-card">
                        <h3>สรุปความเสี่ยง</h3>
                        {user.risk_history && user.risk_history.length > 0 ? (
                            <>
                                <p className="current-risk">
                                    {th.userDetail.userInfo.currentRisk}:
                                    <span className={`badge badge-${user.risk_history[0]?.level?.toLowerCase() || 'low'}`}>
                                        {user.risk_history[0]?.level || 'LOW'}
                                    </span>
                                </p>
                                <div className="risk-factors">
                                    <strong>ปัจจัยล่าสุด:</strong>
                                    <ul>
                                        {user.risk_history[0]?.factors?.map((f, i) => (
                                            <li key={i}>{f}</li>
                                        )) || <li>ไม่มีปัจจัยเฉพาะ</li>}
                                    </ul>
                                </div>
                            </>
                        ) : (
                            <p>ไม่มีข้อมูลความเสี่ยง</p>
                        )}
                    </div>
                </div>

                {/* Mood Chart */}
                <div className="card chart-section">
                    <h3>📊 {th.userDetail.moodHistory}</h3>
                    {user.mood_history && user.mood_history.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={[...user.mood_history].reverse()}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis
                                    dataKey="date"
                                    stroke="#64748b"
                                    fontSize={12}
                                    tickFormatter={(val) => new Date(val).toLocaleDateString('th-TH')}
                                />
                                <YAxis domain={[0, 10]} stroke="#64748b" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1e293b',
                                        border: '1px solid #334155',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="mood_score"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    name="อารมณ์"
                                />
                                <Line
                                    type="monotone"
                                    dataKey="stress_score"
                                    stroke="#ef4444"
                                    strokeWidth={2}
                                    name="ความเครียด"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <p className="no-data">{th.userDetail.noData}</p>
                    )}
                </div>

                {/* Conversation Summary */}
                <div className="card conversation-section">
                    <h3>💬 {th.userDetail.chatHistory}</h3>
                    {user.recent_conversations && user.recent_conversations.length > 0 ? (
                        <div className="conversation-list">
                            {user.recent_conversations.map((msg, index) => (
                                <div key={index} className={`conversation-msg ${msg.role}`}>
                                    <div className="msg-header">
                                        <span className="msg-role">{msg.role === 'user' ? '👤 ผู้ใช้' : '🌿 AI'}</span>
                                        {msg.emotion && (
                                            <span className="msg-emotion">อารมณ์: {msg.emotion}</span>
                                        )}
                                        <span className="msg-time">
                                            {new Date(msg.timestamp).toLocaleString('th-TH')}
                                        </span>
                                    </div>
                                    <p className="msg-content">{msg.message}</p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="no-data">{th.userDetail.noData}</p>
                    )}
                </div>
            </div>
        </div>
    )
}

function getMockUserDetail() {
    return {
        user_id: 'abc123...',
        created_at: '2026-02-01T10:00:00Z',
        consent: true,
        mood_history: [
            { date: '2026-02-01', mood_score: 6, stress_score: 5 },
            { date: '2026-02-02', mood_score: 5, stress_score: 6 },
            { date: '2026-02-03', mood_score: 4, stress_score: 7 },
            { date: '2026-02-04', mood_score: 5, stress_score: 6 },
            { date: '2026-02-05', mood_score: 6, stress_score: 5 },
        ],
        risk_history: [
            { level: 'MEDIUM', score: 45, timestamp: '2026-02-05T15:00:00Z', factors: ['ตรวจพบ sentiment เชิงลบ', 'พบตัวบ่งชี้ความเครียด'] }
        ],
        recent_conversations: [
            { role: 'user', message: "รู้สึกเครียดมากเรื่องสอบ...", emotion: 'fear', timestamp: '2026-02-05T14:30:00Z' },
            { role: 'ai', message: "ฟังดูหนักใจมากเลยนะ ความกดดันจากการสอบเป็นเรื่องที่เข้าใจได้...", timestamp: '2026-02-05T14:30:05Z' },
            { role: 'user', message: "ใช่ รู้สึกว่าตามไม่ทันเลย", emotion: 'sadness', timestamp: '2026-02-05T14:31:00Z' },
            { role: 'ai', message: "เข้าใจเลยที่รู้สึกแบบนั้น อะไรคือส่วนที่ท้าทายที่สุด?", timestamp: '2026-02-05T14:31:05Z' },
        ]
    }
}

export default UserDetail
