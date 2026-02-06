/**
 * API Service
 * Handles all communication with the backend
 */

const API_BASE = '/api';

/**
 * Generic fetch wrapper with error handling
 */
async function fetchAPI(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;

    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    try {
        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || `API Error: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API Error [${endpoint}]:`, error);
        throw error;
    }
}

// ============================================
// User APIs
// ============================================

export async function createUser(anonymousMode = true, consent = true) {
    return fetchAPI('/users', {
        method: 'POST',
        body: JSON.stringify({ anonymous_mode: anonymousMode, consent }),
    });
}

export async function getUser(userId) {
    return fetchAPI(`/users/${userId}`);
}

// ============================================
// Chat APIs
// ============================================

export async function sendMessage(userId, message) {
    return fetchAPI('/chat', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, message }),
    });
}

export async function getChatHistory(userId, limit = 50) {
    return fetchAPI(`/chat/history/${userId}?limit=${limit}`);
}

// ============================================
// Mood APIs
// ============================================

export async function logMood(userId, moodScore, stressScore, notes = null) {
    return fetchAPI('/mood', {
        method: 'POST',
        body: JSON.stringify({
            user_id: userId,
            mood_score: moodScore,
            stress_score: stressScore,
            notes,
        }),
    });
}

export async function getMoodHistory(userId, days = 30) {
    return fetchAPI(`/mood/history/${userId}?days=${days}`);
}

export async function getMoodTrends(userId, days = 14) {
    return fetchAPI(`/mood/trends/${userId}?days=${days}`);
}

export async function submitQuestionnaire(userId, answers) {
    return fetchAPI('/mood/questionnaire', {
        method: 'POST',
        body: JSON.stringify({ user_id: userId, ...answers }),
    });
}

// ============================================
// Risk APIs
// ============================================

export async function getRiskScores(userId, days = 30) {
    return fetchAPI(`/risk/${userId}?days=${days}`);
}

export async function getRiskAnalysis(userId) {
    return fetchAPI(`/risk/${userId}/analysis`);
}

export async function getHighRiskUsers(days = 7) {
    return fetchAPI(`/risk/high-risk-users?days=${days}`);
}

// ============================================
// Dashboard APIs
// ============================================

export async function getDashboard() {
    return fetchAPI('/dashboard');
}

export async function getDashboardUsers(limit = 50, offset = 0) {
    return fetchAPI(`/dashboard/users?limit=${limit}&offset=${offset}`);
}

export async function getUserDetail(userId) {
    return fetchAPI(`/dashboard/user/${userId}`);
}

// ============================================
// Alert APIs
// ============================================

export async function getAlerts(resolved = null, riskLevel = null, days = 30) {
    let query = `?days=${days}`;
    if (resolved !== null) query += `&resolved=${resolved}`;
    if (riskLevel) query += `&risk_level=${riskLevel}`;
    return fetchAPI(`/alerts${query}`);
}

export async function getAlert(alertId) {
    return fetchAPI(`/alerts/${alertId}`);
}

export async function resolveAlert(alertId, notes = null) {
    return fetchAPI(`/alerts/${alertId}/resolve`, {
        method: 'PUT',
        body: JSON.stringify({ notes }),
    });
}

export async function getAlertStats() {
    return fetchAPI('/alerts/stats');
}

export default {
    createUser,
    getUser,
    sendMessage,
    getChatHistory,
    logMood,
    getMoodHistory,
    getMoodTrends,
    submitQuestionnaire,
    getRiskScores,
    getRiskAnalysis,
    getHighRiskUsers,
    getDashboard,
    getDashboardUsers,
    getUserDetail,
    getAlerts,
    getAlert,
    resolveAlert,
    getAlertStats,
};
