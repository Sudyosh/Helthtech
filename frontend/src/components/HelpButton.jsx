import { useState } from 'react'
import { th } from '../i18n/th'
import './HelpButton.css'

function HelpButton() {
    const [showModal, setShowModal] = useState(false)

    return (
        <>
            <button
                className="help-button"
                onClick={() => setShowModal(true)}
                title="ขอความช่วยเหลือ"
            >
                {th.help.button}
            </button>

            {showModal && (
                <div className="help-modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="help-modal" onClick={(e) => e.stopPropagation()}>
                        <div className="help-modal-header">
                            <h2>{th.help.title}</h2>
                            <button className="close-btn" onClick={() => setShowModal(false)}>×</button>
                        </div>

                        <div className="help-message">
                            <p>
                                <strong>{th.help.message}</strong>
                            </p>
                        </div>

                        <div className="help-resources">
                            {th.help.resources.map((resource, index) => (
                                <div key={index} className="resource-card">
                                    <span className="resource-icon">{resource.icon}</span>
                                    <div className="resource-info">
                                        <h4>{resource.name}</h4>
                                        <p>{resource.description}</p>
                                    </div>
                                    {resource.action && (
                                        <a href={resource.action} className="btn btn-primary btn-sm">
                                            {resource.actionText}
                                        </a>
                                    )}
                                </div>
                            ))}
                        </div>

                        <div className="help-footer">
                            <p className="emergency-note">
                                {th.help.emergency}
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </>
    )
}

export default HelpButton
