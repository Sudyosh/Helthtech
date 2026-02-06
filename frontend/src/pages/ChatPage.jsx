import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { sendMessage, getChatHistory } from '../services/api'
import MoodLogger from '../components/MoodLogger'
import HelpButton from '../components/HelpButton'
import { th } from '../i18n/th'
import './ChatPage.css'

function ChatPage({ userId }) {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [showMoodLogger, setShowMoodLogger] = useState(false)
    const [typing, setTyping] = useState(false)
    const messagesEndRef = useRef(null)
    const inputRef = useRef(null)

    // Initial greeting
    useEffect(() => {
        const greeting = {
            role: 'ai',
            message: th.chat.greeting,
            timestamp: new Date().toISOString()
        }
        setMessages([greeting])

        // Try to load chat history
        loadHistory()
    }, [userId])

    const loadHistory = async () => {
        try {
            const history = await getChatHistory(userId, 20)
            if (history.messages && history.messages.length > 0) {
                setMessages(history.messages)
            }
        } catch (error) {
            console.log('Could not load history:', error)
        }
    }

    // Auto-scroll to bottom
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || loading) return

        const userMessage = {
            role: 'user',
            message: input.trim(),
            timestamp: new Date().toISOString()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)
        setTyping(true)

        try {
            const response = await sendMessage(userId, userMessage.message)

            // Simulate typing delay for more natural feel
            await new Promise(resolve => setTimeout(resolve, 500))

            const aiMessage = {
                role: 'ai',
                message: response.ai_response,
                timestamp: response.timestamp,
                emotion: response.emotion,
                risk_level: response.risk_level
            }

            setMessages(prev => [...prev, aiMessage])

            // Show mood logger suggestion occasionally
            if (Math.random() > 0.7 && messages.length > 4) {
                setTimeout(() => {
                    if (!showMoodLogger) {
                        setShowMoodLogger(true)
                    }
                }, 2000)
            }
        } catch (error) {
            console.error('Error sending message:', error)
            // Fallback response
            const fallbackMessage = {
                role: 'ai',
                message: th.chat.fallbackResponse,
                timestamp: new Date().toISOString()
            }
            setMessages(prev => [...prev, fallbackMessage])
        } finally {
            setLoading(false)
            setTyping(false)
            inputRef.current?.focus()
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    const handleMoodLogged = (mood, stress) => {
        const moodMessage = {
            role: 'ai',
            message: th.chat.moodLogged.replace('{mood}', mood).replace('{stress}', stress),
            timestamp: new Date().toISOString(),
            type: 'mood_log'
        }
        setMessages(prev => [...prev, moodMessage])
        setShowMoodLogger(false)
    }

    return (
        <div className="chat-page">
            {/* Header */}
            <header className="chat-header">
                <Link to="/" className="back-btn">
                    {th.chat.backBtn}
                </Link>
                <div className="chat-title">
                    <span className="chat-logo">🌿</span>
                    <div>
                        <h1>{th.appName}</h1>
                        <span className="chat-status">
                            <span className="status-dot"></span>
                            {th.chat.status}
                        </span>
                    </div>
                </div>
                <div className="header-actions">
                    <button
                        className="mood-btn"
                        onClick={() => setShowMoodLogger(!showMoodLogger)}
                        title="บันทึกอารมณ์"
                    >
                        📊
                    </button>
                </div>
            </header>

            {/* Messages */}
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div
                        key={index}
                        className={`message ${msg.role === 'user' ? 'message-user' : 'message-ai'} animate-slideUp`}
                    >
                        {msg.role === 'ai' && (
                            <div className="message-avatar">🌿</div>
                        )}
                        <div className="message-content">
                            <div className="message-bubble">
                                {msg.message}
                            </div>
                            <span className="message-time">
                                {new Date(msg.timestamp).toLocaleTimeString('th-TH', {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                })}
                            </span>
                        </div>
                    </div>
                ))}

                {typing && (
                    <div className="message message-ai animate-fadeIn">
                        <div className="message-avatar">🌿</div>
                        <div className="message-content">
                            <div className="message-bubble typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Mood Logger */}
            {showMoodLogger && (
                <div className="mood-logger-container animate-slideUp">
                    <MoodLogger
                        userId={userId}
                        onMoodLogged={handleMoodLogged}
                        onClose={() => setShowMoodLogger(false)}
                    />
                </div>
            )}

            {/* Input Area */}
            <div className="chat-input-area">
                <div className="chat-input-container">
                    <textarea
                        ref={inputRef}
                        className="chat-input"
                        placeholder={th.chat.placeholder}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        rows={1}
                        disabled={loading}
                    />
                    <button
                        className="send-btn"
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                    >
                        {loading ? '...' : '→'}
                    </button>
                </div>
                <p className="safety-note">
                    {th.chat.privacyNote}
                </p>
            </div>

            {/* Help Button */}
            <HelpButton />
        </div>
    )
}

export default ChatPage
