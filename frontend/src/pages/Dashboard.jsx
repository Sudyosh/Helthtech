import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDashboard, getAlerts, resolveAlert, getDashboardUsers } from '../services/api'
import { th } from '../i18n/th'
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts'
import './Dashboard.css'

const RISK_COLORS = {
    LOW: '#10b981',
    MEDIUM: '#f59e0b',
    HIGH: '#ef4444'
}

function Dashboard() {
    const [data, setData] = useState(null)
    const [alerts, setAlerts] = useState([])
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('overview')

    useEffect(() => {
        loadDashboardData()
    }, [])

    const loadDashboardData = async () => {
        setLoading(true)
        try {
            const [dashData, alertData, userData] = await Promise.all([
                getDashboard().catch(() => null),
                getAlerts(false).catch(() => ({ alerts: [] })),
                getDashboardUsers().catch(() => ({ users: [] }))
            ])

            if (dashData) setData(dashData)
            if (alertData) setAlerts(alertData.alerts || [])
            if (userData) setUsers(userData.users || [])
        } catch (error) {
            console.error('Dashboard load error:', error)
            // Use mock data for demo
            setData(getMockData())
            setAlerts(getMockAlerts())
            setUsers(getMockUsers())
        } finally {
            setLoading(false)
        }
    }

    const handleResolveAlert = async (alertId) => {
        try {
            await resolveAlert(alertId, 'ตรวจสอบโดยผู้เชี่ยวชาญแล้ว')
            setAlerts(prev => prev.filter(a => a.id !== alertId))
        } catch (error) {
            console.error('Error resolving alert:', error)
        }
    }

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
                <p>{th.dashboard.loading}</p>
            </div>
        )
    }

    const riskPieData = data?.risk_distribution ? [
        { name: th.dashboard.charts.lowRisk, value: data.risk_distribution.LOW || 0, color: RISK_COLORS.LOW },
        { name: th.dashboard.charts.mediumRisk, value: data.risk_distribution.MEDIUM || 0, color: RISK_COLORS.MEDIUM },
        { name: th.dashboard.charts.highRisk, value: data.risk_distribution.HIGH || 0, color: RISK_COLORS.HIGH },
    ] : []

    return (
        <div className="dashboard">
            {/* Header */}
            <header className="dashboard-header">
                <div className="header-left">
                    <Link to="/" className="back-btn">{th.dashboard.home}</Link>
                    <h1>{th.dashboard.title}</h1>
                </div>
                <div className="header-right">
                    <span className="last-updated">
                        {th.dashboard.lastUpdated} {new Date().toLocaleTimeString('th-TH')}
                    </span>
                    <button className="btn btn-secondary btn-sm" onClick={loadDashboardData}>
                        {th.dashboard.refresh}
                    </button>
                </div>
            </header>

            {/* Tabs */}
            <nav className="dashboard-tabs">
                <button
                    className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                    onClick={() => setActiveTab('overview')}
                >
                    {th.dashboard.tabs.overview}
                </button>
                <button
                    className={`tab ${activeTab === 'alerts' ? 'active' : ''}`}
                    onClick={() => setActiveTab('alerts')}
                >
                    {th.dashboard.tabs.alerts} {alerts.length > 0 && <span className="badge badge-danger">{alerts.length}</span>}
                </button>
                <button
                    className={`tab ${activeTab === 'users' ? 'active' : ''}`}
                    onClick={() => setActiveTab('users')}
                >
                    {th.dashboard.tabs.users}
                </button>
            </nav>

            <div className="dashboard-content">
                {activeTab === 'overview' && (
                    <>
                        {/* Summary Cards */}
                        <div className="summary-cards">
                            <div className="summary-card">
                                <div className="summary-icon">👥</div>
                                <div className="summary-info">
                                    <h3>{data?.summary?.total_users || 0}</h3>
                                    <p>{th.dashboard.summary.totalUsers}</p>
                                </div>
                            </div>
                            <div className="summary-card">
                                <div className="summary-icon">💬</div>
                                <div className="summary-info">
                                    <h3>{data?.summary?.active_users || 0}</h3>
                                    <p>{th.dashboard.summary.activeUsers}</p>
                                </div>
                            </div>
                            <div className="summary-card warning">
                                <div className="summary-icon">⚠️</div>
                                <div className="summary-info">
                                    <h3>{data?.summary?.high_risk_users || 0}</h3>
                                    <p>{th.dashboard.summary.highRiskUsers}</p>
                                </div>
                            </div>
                            <div className="summary-card danger">
                                <div className="summary-icon">🚨</div>
                                <div className="summary-info">
                                    <h3>{data?.summary?.unresolved_alerts || alerts.length}</h3>
                                    <p>{th.dashboard.summary.unresolvedAlerts}</p>
                                </div>
                            </div>
                        </div>

                        {/* Charts Grid */}
                        <div className="charts-grid">
                            {/* Mood Trends Chart */}
                            <div className="card chart-card">
                                <div className="card-header">
                                    <h3 className="card-title">{th.dashboard.charts.moodTrends}</h3>
                                </div>
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={250}>
                                        <LineChart data={data?.mood_trends || getMockMoodTrends()}>
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
                                            <Line
                                                type="monotone"
                                                dataKey="average_mood"
                                                stroke="#10b981"
                                                strokeWidth={2}
                                                name={th.dashboard.charts.avgMood}
                                                dot={{ fill: '#10b981' }}
                                            />
                                            <Line
                                                type="monotone"
                                                dataKey="average_stress"
                                                stroke="#ef4444"
                                                strokeWidth={2}
                                                name={th.dashboard.charts.avgStress}
                                                dot={{ fill: '#ef4444' }}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Risk Distribution */}
                            <div className="card chart-card">
                                <div className="card-header">
                                    <h3 className="card-title">{th.dashboard.charts.riskDistribution}</h3>
                                </div>
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={250}>
                                        <PieChart>
                                            <Pie
                                                data={riskPieData.length > 0 ? riskPieData : getMockRiskData()}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={60}
                                                outerRadius={80}
                                                paddingAngle={5}
                                                dataKey="value"
                                                label
                                            >
                                                {(riskPieData.length > 0 ? riskPieData : getMockRiskData()).map((entry, index) => (
                                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                                ))}
                                            </Pie>
                                            <Tooltip />
                                            <Legend />
                                        </PieChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Emotion Distribution */}
                            <div className="card chart-card wide">
                                <div className="card-header">
                                    <h3 className="card-title">{th.dashboard.charts.emotionDistribution}</h3>
                                </div>
                                <div className="chart-container">
                                    <ResponsiveContainer width="100%" height={250}>
                                        <BarChart data={data?.emotion_distribution || getMockEmotions()}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                            <XAxis dataKey="emotion" stroke="#64748b" fontSize={12} />
                                            <YAxis stroke="#64748b" fontSize={12} />
                                            <Tooltip
                                                contentStyle={{
                                                    background: '#1e293b',
                                                    border: '1px solid #334155',
                                                    borderRadius: '8px'
                                                }}
                                            />
                                            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'alerts' && (
                    <div className="alerts-section">
                        <h2>{th.dashboard.alerts.title}</h2>
                        {alerts.length === 0 ? (
                            <div className="empty-state">
                                <span className="empty-icon">✅</span>
                                <p>{th.dashboard.alerts.empty}</p>
                            </div>
                        ) : (
                            <div className="alerts-list">
                                {alerts.map(alert => (
                                    <div key={alert.id} className={`alert-card risk-${alert.risk_level.toLowerCase()}`}>
                                        <div className="alert-header">
                                            <span className={`badge badge-${alert.risk_level.toLowerCase()}`}>
                                                {alert.risk_level}
                                            </span>
                                            <span className="alert-time">
                                                {new Date(alert.created_at).toLocaleString('th-TH')}
                                            </span>
                                        </div>
                                        <div className="alert-body">
                                            <p className="alert-user">{th.dashboard.alerts.user} {alert.user_id}</p>
                                            <p className="alert-trigger">
                                                <strong>{th.dashboard.alerts.trigger}</strong> "{alert.trigger_message}"
                                            </p>
                                        </div>
                                        <div className="alert-actions">
                                            <Link
                                                to={`/dashboard/user/${alert.user_id}`}
                                                className="btn btn-secondary btn-sm"
                                            >
                                                {th.dashboard.alerts.viewDetails}
                                            </Link>
                                            <button
                                                className="btn btn-primary btn-sm"
                                                onClick={() => handleResolveAlert(alert.id)}
                                            >
                                                {th.dashboard.alerts.markResolved}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'users' && (
                    <div className="users-section">
                        <h2>{th.dashboard.users.title}</h2>
                        <div className="users-table-container">
                            <table className="users-table">
                                <thead>
                                    <tr>
                                        <th>{th.dashboard.users.userId}</th>
                                        <th>{th.dashboard.users.riskLevel}</th>
                                        <th>{th.dashboard.users.lastMood}</th>
                                        <th>{th.dashboard.users.lastStress}</th>
                                        <th>{th.dashboard.users.created}</th>
                                        <th>{th.dashboard.users.actions}</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {(users.length > 0 ? users : getMockUsers()).map(user => (
                                        <tr key={user.user_id || user.full_id}>
                                            <td className="user-id">{user.user_id}</td>
                                            <td>
                                                <span className={`badge badge-${(user.current_risk_level || 'low').toLowerCase()}`}>
                                                    {user.current_risk_level || 'LOW'}
                                                </span>
                                            </td>
                                            <td>{user.latest_mood || '-'}</td>
                                            <td>{user.latest_stress || '-'}</td>
                                            <td>{user.created_at ? new Date(user.created_at).toLocaleDateString('th-TH') : '-'}</td>
                                            <td>
                                                <Link
                                                    to={`/dashboard/user/${user.full_id || user.user_id}`}
                                                    className="btn btn-secondary btn-sm"
                                                >
                                                    {th.dashboard.users.view}
                                                </Link>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

// Mock data functions for demo
function getMockData() {
    return {
        summary: {
            total_users: 47,
            active_users: 23,
            high_risk_users: 3,
            unresolved_alerts: 5
        },
        mood_trends: getMockMoodTrends(),
        risk_distribution: { LOW: 35, MEDIUM: 9, HIGH: 3 },
        emotion_distribution: getMockEmotions()
    }
}

function getMockMoodTrends() {
    return [
        { date: '1 ก.พ.', average_mood: 6.2, average_stress: 5.8 },
        { date: '2 ก.พ.', average_mood: 5.9, average_stress: 6.1 },
        { date: '3 ก.พ.', average_mood: 6.5, average_stress: 5.5 },
        { date: '4 ก.พ.', average_mood: 6.1, average_stress: 5.9 },
        { date: '5 ก.พ.', average_mood: 6.8, average_stress: 5.2 },
        { date: '6 ก.พ.', average_mood: 6.4, average_stress: 5.6 },
    ]
}

function getMockRiskData() {
    return [
        { name: th.dashboard.charts.lowRisk, value: 35, color: RISK_COLORS.LOW },
        { name: th.dashboard.charts.mediumRisk, value: 9, color: RISK_COLORS.MEDIUM },
        { name: th.dashboard.charts.highRisk, value: 3, color: RISK_COLORS.HIGH },
    ]
}

function getMockEmotions() {
    return [
        { emotion: 'ปกติ', count: 45 },
        { emotion: 'เศร้า', count: 28 },
        { emotion: 'มีความสุข', count: 22 },
        { emotion: 'กลัว', count: 15 },
        { emotion: 'โกรธ', count: 10 },
    ]
}

function getMockAlerts() {
    return [
        {
            id: '1',
            user_id: 'abc123...',
            risk_level: 'HIGH',
            trigger_message: "ไม่รู้จะทนไปต่อได้อีกนานแค่ไหน...",
            created_at: new Date().toISOString(),
            resolved: false
        },
        {
            id: '2',
            user_id: 'def456...',
            risk_level: 'MEDIUM',
            trigger_message: "รู้สึกสิ้นหวังกับทุกอย่าง",
            created_at: new Date(Date.now() - 3600000).toISOString(),
            resolved: false
        }
    ]
}

function getMockUsers() {
    return [
        { user_id: 'abc123...', full_id: 'abc123-full', current_risk_level: 'HIGH', latest_mood: 4, latest_stress: 8, created_at: '2026-02-01' },
        { user_id: 'def456...', full_id: 'def456-full', current_risk_level: 'MEDIUM', latest_mood: 5, latest_stress: 6, created_at: '2026-02-02' },
        { user_id: 'ghi789...', full_id: 'ghi789-full', current_risk_level: 'LOW', latest_mood: 7, latest_stress: 3, created_at: '2026-02-03' },
        { user_id: 'jkl012...', full_id: 'jkl012-full', current_risk_level: 'LOW', latest_mood: 8, latest_stress: 2, created_at: '2026-02-04' },
    ]
}

export default Dashboard
