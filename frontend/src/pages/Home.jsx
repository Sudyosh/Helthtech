import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createUser } from '../services/api'
import { th } from '../i18n/th'
import './Home.css'

function Home({ onUserCreated, userId }) {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [consent, setConsent] = useState(false)

    const handleStart = async () => {
        if (userId) {
            navigate('/chat')
            return
        }

        if (!consent) {
            alert('กรุณายอมรับเงื่อนไขเพื่อดำเนินการต่อ')
            return
        }

        setLoading(true)
        try {
            const user = await createUser(true, true)
            onUserCreated(user.user_id)
            navigate('/chat')
        } catch (error) {
            console.error('Failed to create user:', error)
            // For demo, use a mock ID
            const mockId = 'demo-' + Date.now()
            onUserCreated(mockId)
            navigate('/chat')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="home">
            <div className="home-bg">
                <div className="home-orb home-orb-1"></div>
                <div className="home-orb home-orb-2"></div>
                <div className="home-orb home-orb-3"></div>
            </div>

            <div className="home-content">
                <div className="home-hero">
                    <div className="home-logo">
                        <span className="logo-icon">🌿</span>
                        <span className="logo-text">{th.appName}</span>
                    </div>

                    <h1 className="home-title">
                        {th.home.tagline} <span className="gradient-text">{th.home.taglineHighlight}</span>
                    </h1>

                    <p className="home-description">
                        {th.home.description}
                    </p>

                    <div className="home-features">
                        <div className="feature">
                            <span className="feature-icon">💭</span>
                            <span>{th.home.features.chat}</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">📊</span>
                            <span>{th.home.features.mood}</span>
                        </div>
                        <div className="feature">
                            <span className="feature-icon">🔒</span>
                            <span>{th.home.features.private}</span>
                        </div>
                    </div>

                    {!userId && (
                        <div className="consent-box">
                            <label className="consent-label">
                                <input
                                    type="checkbox"
                                    checked={consent}
                                    onChange={(e) => setConsent(e.target.checked)}
                                    className="consent-checkbox"
                                />
                                <span>{th.home.consent}</span>
                            </label>
                        </div>
                    )}

                    <button
                        className="btn btn-primary btn-lg start-btn"
                        onClick={handleStart}
                        disabled={loading || (!userId && !consent)}
                    >
                        {loading ? (
                            <>
                                <span className="loading-spinner"></span>
                                {th.home.starting}
                            </>
                        ) : userId ? (
                            th.home.continueButton
                        ) : (
                            th.home.startButton
                        )}
                    </button>

                    <div className="home-links">
                        <a href="/dashboard" className="home-link">
                            {th.home.dashboardLink}
                        </a>
                    </div>
                </div>

                <div className="home-preview">
                    <div className="chat-preview">
                        <div className="preview-message preview-ai">
                            <span className="preview-avatar">🌿</span>
                            <div className="preview-bubble">
                                สวัสดี! ฉันพร้อมรับฟังนะ วันนี้เป็นยังไงบ้าง?
                            </div>
                        </div>
                        <div className="preview-message preview-user">
                            <div className="preview-bubble">
                                ช่วงนี้เครียดเรื่องเรียนมากเลย...
                            </div>
                        </div>
                        <div className="preview-message preview-ai">
                            <span className="preview-avatar">🌿</span>
                            <div className="preview-bubble">
                                ฟังดูหนักใจนะ ความกดดันจากการเรียนเป็นเรื่องที่เข้าใจได้
                                อยากเล่าให้ฟังเพิ่มไหมว่าอะไรที่ทำให้เครียด?
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <footer className="home-footer">
                <p className="crisis-notice">
                    {th.home.crisisNotice}
                </p>
            </footer>
        </div>
    )
}

export default Home
