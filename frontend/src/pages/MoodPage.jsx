import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getMoodHistory, getMoodTrends, logMood } from '../services/api'
import { th } from '../i18n/th'
import {
    LineChart, Line, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import './MoodPage.css'

function MoodPage({ userId }) {
    const [moodHistory, setMoodHistory] = useState([])
    const [trends, setTrends] = useState([])
    const [loading, setLoading] = useState(true)
    const [showLogger, setShowLogger] = useState(false)
    const [mood, setMood] = useState(5)
    const [stress, setStress] = useState(5)
    const [notes, setNotes] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [timeRange, setTimeRange] = useState(14) // days

    useEffect(() => {
        loadData()
    }, [userId, timeRange])

    const loadData = async () => {
        setLoading(true)
        try {
            const [historyData, trendData] = await Promise.all([
                getMoodHistory(userId, timeRange).catch(() => ({ entries: [] })),
                getMoodTrends(userId, timeRange).catch(() => ({ trends: [] }))
            ])
            setMoodHistory(historyData.entries || getMockHistory())
            setTrends(trendData.trends || getMockTrends())
        } catch (error) {
            console.error('Error loading mood data:', error)
            setMoodHistory(getMockHistory())
            setTrends(getMockTrends())
        } finally {
            setLoading(false)
        }
    }

    const handleLogMood = async () => {
        setSubmitting(true)
        try {
            await logMood(userId, mood, stress, notes || null)
            setShowLogger(false)
            setNotes('')
            loadData()
        } catch (error) {
            console.error('Error logging mood:', error)
        } finally {
            setSubmitting(false)
        }
    }

    const getMoodEmoji = (value) => {
        if (value <= 2) return '😢'
        if (value <= 4) return '😔'
        if (value <= 6) return '😐'
        if (value <= 8) return '🙂'
        return '😊'
    }

    const getStressEmoji = (value) => {
        if (value <= 2) return '😌'
        if (value <= 4) return '🙂'
        if (value <= 6) return '😕'
        if (value <= 8) return '😰'
        return '😫'
    }

    // Calculate averages
    const avgMood = moodHistory.length > 0
        ? (moodHistory.reduce((sum, m) => sum + m.mood_score, 0) / moodHistory.length).toFixed(1)
        : '-'
    const avgStress = moodHistory.length > 0
        ? (moodHistory.reduce((sum, m) => sum + m.stress_score, 0) / moodHistory.length).toFixed(1)
        : '-'

    if (loading) {
        return (
            <div className="mood-page-loading">
                <div className="loading-spinner"></div>
                <p>กำลังโหลดข้อมูล...</p>
            </div>
        )
    }

    return (
        <div className="mood-page">
            <header className="mood-header">
                <Link to="/chat" className="back-btn">← กลับไปแชท</Link>
                <h1>📊 ติดตามอารมณ์</h1>
                <button
                    className="btn btn-primary"
                    onClick={() => setShowLogger(!showLogger)}
                >
                    ➕ บันทึกอารมณ์
                </button>
            </header>

            {/* Quick Log */}
            {showLogger && (
                <div className="quick-logger card animate-slideDown">
                    <h3>📊 วันนี้รู้สึกอย่างไร?</h3>

                    <div className="logger-sliders">
                        <div className="slider-group">
                            <label>
                                อารมณ์: {getMoodEmoji(mood)} {mood}/10
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={mood}
                                onChange={(e) => setMood(parseInt(e.target.value))}
                                className="slider mood-slider"
                            />
                            <div className="slider-labels">
                                <span>แย่มาก</span>
                                <span>ดีมาก</span>
                            </div>
                        </div>

                        <div className="slider-group">
                            <label>
                                ความเครียด: {getStressEmoji(stress)} {stress}/10
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                value={stress}
                                onChange={(e) => setStress(parseInt(e.target.value))}
                                className="slider stress-slider"
                            />
                            <div className="slider-labels">
                                <span>ผ่อนคลาย</span>
                                <span>เครียดมาก</span>
                            </div>
                        </div>
                    </div>

                    <textarea
                        placeholder="หมายเหตุ (ไม่บังคับ)"
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="notes-input"
                        rows={2}
                    />

                    <div className="logger-actions">
                        <button
                            className="btn btn-secondary"
                            onClick={() => setShowLogger(false)}
                        >
                            ยกเลิก
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={handleLogMood}
                            disabled={submitting}
                        >
                            {submitting ? 'กำลังบันทึก...' : 'บันทึก'}
                        </button>
                    </div>
                </div>
            )}

            <div className="mood-content">
                {/* Summary Cards */}
                <div className="summary-row">
                    <div className="summary-card">
                        <span className="summary-emoji">{getMoodEmoji(parseFloat(avgMood) || 5)}</span>
                        <div className="summary-info">
                            <h3>{avgMood}</h3>
                            <p>อารมณ์เฉลี่ย</p>
                        </div>
                    </div>
                    <div className="summary-card">
                        <span className="summary-emoji">{getStressEmoji(parseFloat(avgStress) || 5)}</span>
                        <div className="summary-info">
                            <h3>{avgStress}</h3>
                            <p>ความเครียดเฉลี่ย</p>
                        </div>
                    </div>
                    <div className="summary-card">
                        <span className="summary-emoji">📝</span>
                        <div className="summary-info">
                            <h3>{moodHistory.length}</h3>
                            <p>จำนวนบันทึก</p>
                        </div>
                    </div>
                </div>

                {/* Time Range Selector */}
                <div className="time-range-selector">
                    <button
                        className={`range-btn ${timeRange === 7 ? 'active' : ''}`}
                        onClick={() => setTimeRange(7)}
                    >
                        7 วัน
                    </button>
                    <button
                        className={`range-btn ${timeRange === 14 ? 'active' : ''}`}
                        onClick={() => setTimeRange(14)}
                    >
                        14 วัน
                    </button>
                    <button
                        className={`range-btn ${timeRange === 30 ? 'active' : ''}`}
                        onClick={() => setTimeRange(30)}
                    >
                        30 วัน
                    </button>
                </div>

                {/* Trend Chart */}
                <div className="card chart-card">
                    <h3>📈 แนวโน้มอารมณ์และความเครียด</h3>
                    {trends.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <AreaChart data={trends}>
                                <defs>
                                    <linearGradient id="moodGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="stressGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                                <YAxis domain={[0, 10]} stroke="#64748b" fontSize={12} />
                                <Tooltip
                                    contentStyle={{
                                        background: '#1e293b',
                                        border: '1px solid #334155',
                                        borderRadius: '8px'
                                    }}
                                />
                                <Legend />
                                <Area
                                    type="monotone"
                                    dataKey="mood_score"
                                    stroke="#10b981"
                                    fillOpacity={1}
                                    fill="url(#moodGradient)"
                                    name="อารมณ์"
                                />
                                <Area
                                    type="monotone"
                                    dataKey="stress_score"
                                    stroke="#ef4444"
                                    fillOpacity={1}
                                    fill="url(#stressGradient)"
                                    name="ความเครียด"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    ) : (
                        <p className="no-data">ยังไม่มีข้อมูลเพียงพอ เริ่มบันทึกอารมณ์เลย!</p>
                    )}
                </div>

                {/* History List */}
                <div className="card history-card">
                    <h3>📋 ประวัติการบันทึก</h3>
                    {moodHistory.length > 0 ? (
                        <div className="history-list">
                            {moodHistory.slice(0, 10).map((entry, index) => (
                                <div key={index} className="history-item">
                                    <div className="history-date">
                                        {new Date(entry.date || entry.timestamp).toLocaleDateString('th-TH', {
                                            weekday: 'short',
                                            day: 'numeric',
                                            month: 'short'
                                        })}
                                    </div>
                                    <div className="history-scores">
                                        <span className="mood-score">
                                            {getMoodEmoji(entry.mood_score)} {entry.mood_score}
                                        </span>
                                        <span className="stress-score">
                                            {getStressEmoji(entry.stress_score)} {entry.stress_score}
                                        </span>
                                    </div>
                                    {entry.notes && (
                                        <div className="history-notes">{entry.notes}</div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="no-data">ยังไม่มีประวัติ</p>
                    )}
                </div>
            </div>
        </div>
    )
}

// Mock data
function getMockHistory() {
    return [
        { date: '2026-02-06', mood_score: 7, stress_score: 4, notes: 'วันนี้ดี' },
        { date: '2026-02-05', mood_score: 6, stress_score: 5, notes: null },
        { date: '2026-02-04', mood_score: 5, stress_score: 6, notes: 'เครียดเรื่องงาน' },
        { date: '2026-02-03', mood_score: 6, stress_score: 5, notes: null },
        { date: '2026-02-02', mood_score: 7, stress_score: 4, notes: 'พักผ่อนดี' },
    ]
}

function getMockTrends() {
    return [
        { date: '1 ก.พ.', mood_score: 6, stress_score: 5 },
        { date: '2 ก.พ.', mood_score: 7, stress_score: 4 },
        { date: '3 ก.พ.', mood_score: 6, stress_score: 5 },
        { date: '4 ก.พ.', mood_score: 5, stress_score: 6 },
        { date: '5 ก.พ.', mood_score: 6, stress_score: 5 },
        { date: '6 ก.พ.', mood_score: 7, stress_score: 4 },
    ]
}

export default MoodPage
