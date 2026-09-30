import { useState, useEffect } from 'react';
import { Trophy, Clock, Star, Coins, Copy, Check, TrendingUp } from 'lucide-react';
import api, { getTelegramId } from '../lib/api';
import './ProfilePage.css';

export default function ProfilePage() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);

    useEffect(() => { loadProfile(); }, []);

    const loadProfile = async () => {
        try {
            const telegramId = getTelegramId();
            const response = await api.get(`/client_info/${telegramId}/`);
            setProfile(response.data);
        } catch (error) {
            console.error('Error loading profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const copyCode = () => {
        if (profile?.referral_code) {
            navigator.clipboard.writeText(profile.referral_code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const getRankIcon = (rank) => {
        const ranks = { 'Новичок': '🌱', 'Постоянный': '⭐', 'VIP': '👑', 'Легенда': '🔥' };
        return ranks[rank] || '🎮';
    };

    const getRankProgress = (hours) => {
        const thresholds = [0, 10, 50, 200];
        const labels = ['Новичок', 'Постоянный', 'VIP', 'Легенда'];
        let idx = 0;
        for (let i = thresholds.length - 1; i >= 0; i--) {
            if (hours >= thresholds[i]) { idx = i; break; }
        }
        const next = idx < thresholds.length - 1 ? thresholds[idx + 1] : thresholds[idx];
        const prev = thresholds[idx];
        const pct = idx >= thresholds.length - 1 ? 100 : Math.min(((hours - prev) / (next - prev)) * 100, 100);
        const nextLabel = idx < labels.length - 1 ? labels[idx + 1] : null;
        return { pct: Math.round(pct), nextRank: nextLabel, hoursNeeded: Math.max(0, next - hours) };
    };

    if (loading) return <div className="container"><div className="loading">Загрузка профиля...</div></div>;

    if (!profile) return (
        <div className="container">
            <div className="error-message">
                <div style={{ fontSize: 48, marginBottom: 16 }}>😔</div>
                <p style={{ fontSize: 18, fontWeight: 700 }}>Профиль не найден</p>
                <p className="hint">Используйте /start в боте для регистрации</p>
            </div>
        </div>
    );

    const progress = getRankProgress(parseFloat(profile.total_hours_played) || 0);

    return (
        <div className="container profile-page">
            {/* Profile Header */}
            <div className="profile-hero animate-fade-in">
                <div className="hero-bg"></div>
                <div className="avatar-wrapper">
                    <div className="avatar">{profile.name.charAt(0).toUpperCase()}</div>
                    <div className="avatar-ring"></div>
                </div>
                <h1 className="profile-name">{profile.name}</h1>
                <div className="rank-badge">
                    <span>{getRankIcon(profile.rank)}</span>
                    <span>{profile.rank}</span>
                </div>
            </div>

            {/* Rank Progress */}
            {progress.nextRank && (
                <div className="card progress-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
                    <div className="progress-header">
                        <TrendingUp size={16} style={{ color: 'var(--primary-light)' }} />
                        <span>До ранга «{progress.nextRank}»</span>
                    </div>
                    <div className="progress-bar-wrap">
                        <div className="progress-bar" style={{ width: `${progress.pct}%` }}></div>
                    </div>
                    <div className="progress-info">
                        <span>{progress.pct}%</span>
                        <span>Ещё {progress.hoursNeeded.toFixed(0)}ч</span>
                    </div>
                </div>
            )}

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card animate-fade-in" style={{ animationDelay: '0.15s' }}>
                    <Coins className="stat-icon" style={{ color: '#fbbf24' }} />
                    <div className="stat-value">{profile.bonus_points}</div>
                    <div className="stat-label">Бонусы</div>
                </div>
                <div className="stat-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <Clock className="stat-icon" style={{ color: '#818cf8' }} />
                    <div className="stat-value">{profile.total_hours_played}ч</div>
                    <div className="stat-label">Всего часов</div>
                </div>
                <div className="stat-card animate-fade-in" style={{ animationDelay: '0.25s' }}>
                    <Trophy className="stat-icon" style={{ color: '#ec4899' }} />
                    <div className="stat-value">{profile.referrals_count || 0}</div>
                    <div className="stat-label">Рефералов</div>
                </div>
                <div className="stat-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
                    <Star className="stat-icon" style={{ color: '#10b981' }} />
                    <div className="stat-value">{Math.round((parseFloat(profile.bonus_points) || 0) * 0.01)}₽</div>
                    <div className="stat-label">Кэшбэк</div>
                </div>
            </div>

            {/* Referral Code */}
            <div className="card referral-card animate-fade-in" style={{ animationDelay: '0.35s' }}>
                <h3>🎁 Ваш реферальный код</h3>
                <div className="referral-code-row">
                    <div className="referral-code">{profile.referral_code || 'N/A'}</div>
                    <button className="btn-copy" onClick={copyCode}>
                        {copied ? <Check size={20} /> : <Copy size={20} />}
                    </button>
                </div>
                <p className="hint">Поделитесь кодом — получите 100 бонусов!</p>
            </div>
        </div>
    );
}
