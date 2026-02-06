import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Home from './pages/Home'
import ChatPage from './pages/ChatPage'
import Dashboard from './pages/Dashboard'
import UserDetail from './pages/UserDetail'
import MoodPage from './pages/MoodPage'
import { createUser, getUser } from './services/api'

function App() {
    const [userId, setUserId] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        // Check for existing user ID in localStorage
        const storedUserId = localStorage.getItem('userId')
        if (storedUserId) {
            setUserId(storedUserId)
        }
        setLoading(false)
    }, [])

    const handleUserCreated = (newUserId) => {
        localStorage.setItem('userId', newUserId)
        setUserId(newUserId)
    }

    if (loading) {
        return (
            <div className="loading-screen">
                <div className="loading-spinner"></div>
                <p>Loading...</p>
            </div>
        )
    }

    return (
        <BrowserRouter>
            <div className="app">
                <Routes>
                    <Route
                        path="/"
                        element={<Home onUserCreated={handleUserCreated} userId={userId} />}
                    />
                    <Route
                        path="/chat"
                        element={userId ? <ChatPage userId={userId} /> : <Navigate to="/" />}
                    />
                    <Route path="/dashboard" element={<Dashboard />} />
                    <Route path="/dashboard/user/:userId" element={<UserDetail />} />
                    <Route
                        path="/mood"
                        element={userId ? <MoodPage userId={userId} /> : <Navigate to="/" />}
                    />
                </Routes>
            </div>
        </BrowserRouter>
    )
}

export default App
