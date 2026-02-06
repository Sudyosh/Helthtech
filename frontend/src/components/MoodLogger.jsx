import { useState } from 'react'
import { logMood } from '../services/api'
import { th } from '../i18n/th'
import './MoodLogger.css'

function MoodLogger({ userId, onMoodLogged, onClose }) {
    const [mood, setMood] = useState(5)
    const [stress, setStress] = useState(5)
    const [notes, setNotes] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async () => {
        setLoading(true)
        try {
            await logMood(userId, mood, stress, notes || null)
            onMoodLogged(mood, stress)
        } catch (error) {
            console.error('Error logging mood:', error)
            // Still notify parent for demo purposes
            onMoodLogged(mood, stress)
        } finally {
            setLoading(false)
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

    return (
        <div className="mood-logger">
            <div className="mood-logger-header">
                <h3>{th.mood.title}</h3>
                <button className="close-btn" onClick={onClose}>×</button>
            </div>

            <div className="mood-slider">
                <label>
                    <span className="slider-label">
                        {th.mood.moodLabel}: {getMoodEmoji(mood)} {mood}/10
                    </span>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={mood}
                        onChange={(e) => setMood(parseInt(e.target.value))}
                        className="slider mood-slider-input"
                    />
                    <div className="slider-labels">
                        <span>{th.mood.veryLow}</span>
                        <span>{th.mood.great}</span>
                    </div>
                </label>
            </div>

            <div className="mood-slider">
                <label>
                    <span className="slider-label">
                        {th.mood.stressLabel}: {getStressEmoji(stress)} {stress}/10
                    </span>
                    <input
                        type="range"
                        min="1"
                        max="10"
                        value={stress}
                        onChange={(e) => setStress(parseInt(e.target.value))}
                        className="slider stress-slider-input"
                    />
                    <div className="slider-labels">
                        <span>{th.mood.relaxed}</span>
                        <span>{th.mood.veryStressed}</span>
                    </div>
                </label>
            </div>

            <div className="notes-section">
                <label>
                    <span className="notes-label">{th.mood.notesLabel}</span>
                    <textarea
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        placeholder={th.mood.notesPlaceholder}
                        className="notes-input"
                        rows={2}
                    />
                </label>
            </div>

            <button
                className="btn btn-primary w-full"
                onClick={handleSubmit}
                disabled={loading}
            >
                {loading ? th.mood.saving : th.mood.saveButton}
            </button>
        </div>
    )
}

export default MoodLogger
