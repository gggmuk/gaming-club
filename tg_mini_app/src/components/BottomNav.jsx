import { Home, User, Gift, Calendar } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import './BottomNav.css';

export default function BottomNav() {
    const navigate = useNavigate();
    const location = useLocation();

    const tabs = [
        { icon: Home, label: 'Главная', path: '/' },
        { icon: Calendar, label: 'Брони', path: '/bookings' },
        { icon: Gift, label: 'Рефералы', path: '/referrals' },
        { icon: User, label: 'Профиль', path: '/profile' },
    ];

    return (
        <nav className="bottom-nav">
            {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = location.pathname === tab.path;
                return (
                    <button
                        key={tab.path}
                        className={`nav-item ${isActive ? 'active' : ''}`}
                        onClick={() => navigate(tab.path)}
                    >
                        <div className="nav-icon-wrap">
                            <Icon size={22} />
                            {isActive && <div className="nav-active-dot" />}
                        </div>
                        <span>{tab.label}</span>
                    </button>
                );
            })}
        </nav>
    );
}
