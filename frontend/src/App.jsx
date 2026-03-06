import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import ScanPage from './pages/ScanPage';
import ProfilePage from './pages/ProfilePage';

function App() {
    return (
        <Router>
            <div>
                <nav style={{ padding: '10px', borderBottom: '1px solid #ccc' }}>
                    <Link to="/" style={{ marginRight: '10px' }}>Home</Link>
                    <Link to="/scan" style={{ marginRight: '10px' }}>Scan</Link>
                    <Link to="/profile">Profile</Link>
                </nav>

                <div style={{ padding: '20px' }}>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/scan" element={<ScanPage />} />
                        <Route path="/profile" element={<ProfilePage />} />
                    </Routes>
                </div>
            </div>
        </Router>
    );
}

export default App;
