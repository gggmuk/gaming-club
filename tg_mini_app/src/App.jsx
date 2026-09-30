import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ProfilePage from './pages/ProfilePage';
import ReferralsPage from './pages/ReferralsPage';
import BookingsPage from './pages/BookingsPage';
import BottomNav from './components/BottomNav';
import './index.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/referrals" element={<ReferralsPage />} />
          <Route path="/bookings" element={<BookingsPage />} />
        </Routes>
        <BottomNav />
      </div>
    </Router>
  );
}

export default App;
