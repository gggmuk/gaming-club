import { useState, useEffect } from 'react';
import { Users, Copy, Check, Gift, Share2 } from 'lucide-react';
import api, { getTelegramId } from '../lib/api';
import './ReferralsPage.css';

export default function ReferralsPage() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);
    const [referralInput, setReferralInput] = useState('');
    const [applying, setApplying] = useState(false);

    useEffect(() => { loadReferralStats(); }, []);

    const loadReferralStats = async () => {
        try {
            const telegramId = getTelegramId();
            const response = await api.get(`/referral_stats/${telegramId}/`);
            setStats(response.data);
        } catch (error) {
            console.error('Error loading referral stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const copyReferralCode = () => {
        if (stats?.referral_code) {
            navigator.clipboard.writeText(stats.referral_code);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    const shareCode = () => {
        if (stats?.referral_code && navigator.share) {
            navigator.share({
                title: 'CyberLounge — Приглашение',
                text: `Присоединяйся к CyberLounge! Мой реферальный код: ${stats.referral_code}. Получи бонусы при регистрации!`,
            }).catch(() => {});
        } else {
            copyReferralCode();
        }
    };

    const applyReferral = async () => {
        if (!referralInput.trim()) return;
        setApplying(true);
        try {
            const telegramId = getTelegramId();
            await api.post('/apply_referral/', {
                telegram_id: telegramId,
                referral_code: referralInput.trim().toUpperCase()
            });
            setReferralInput('');
            loadReferralStats();
        } catch (error) {
            const msg = error.response?.data?.error || 'Ошибка';
            alert('❌ ' + msg);
        } finally {
            setApplying(false);
        }
    };

    if (loading) return <div className="container"><div className="loading">Загрузка...</div></div>;

    return (
        <div className="container referrals-page">
            <h1 className="page-title">🎁 Реферальная программа</h1>

            {/* How it works */}
            <div className="card how-it-works animate-fade-in">
                <h3>Как это работает?</h3>
                <div className="steps">
                    <div className="step"><div className="step-num">1</div><span>Поделитесь кодом с другом</span></div>
                    <div className="step"><div className="step-num">2</div><span>Друг регистрируется с вашим кодом</span></div>
                    <div className="step"><div className="step-num">3</div><span>Вы получаете <strong>100 бонусов</strong>!</span></div>
                </div>
            </div>

            {/* Your Code */}
            <div className="card code-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
                <h3>Ваш реферальный код</h3>
                <div className="code-display">{stats?.referral_code || 'N/A'}</div>
                <div className="code-actions">
                    <button className="btn-action" onClick={copyReferralCode}>
                        {copied ? <><Check size={18} /> Скопировано!</> : <><Copy size={18} /> Копировать</>}
                    </button>
                    <button className="btn-action btn-share" onClick={shareCode}>
                        <Share2 size={18} /> Поделиться
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="card stats-row-card animate-fade-in" style={{ animationDelay: '0.15s' }}>
                <div className="ref-stat">
                    <Users size={28} style={{ color: 'var(--primary-light)' }} />
                    <div className="ref-stat-val">{stats?.referrals_count || 0}</div>
                    <div className="ref-stat-label">Приглашено друзей</div>
                </div>
                <div className="ref-stat">
                    <Gift size={28} style={{ color: '#fbbf24' }} />
                    <div className="ref-stat-val">{(stats?.referrals_count || 0) * 100}</div>
                    <div className="ref-stat-label">Бонусов получено</div>
                </div>
            </div>

            {/* Apply Code */}
            <div className="card apply-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <h3>Ввести код друга</h3>
                <div className="apply-row">
                    <input
                        type="text"
                        className="input"
                        placeholder="Введите код..."
                        value={referralInput}
                        onChange={e => setReferralInput(e.target.value.toUpperCase())}
                        style={{ marginBottom: 0 }}
                        maxLength={10}
                    />
                    <button
                        className="btn btn-apply"
                        onClick={applyReferral}
                        disabled={applying || !referralInput.trim()}
                    >
                        {applying ? '...' : 'Применить'}
                    </button>
                </div>
            </div>

            {/* Referrals List */}
            {stats?.referrals && stats.referrals.length > 0 && (
                <div className="referrals-list animate-fade-in" style={{ animationDelay: '0.25s' }}>
                    <h3>Ваши рефералы</h3>
                    {stats.referrals.map((referral, index) => (
                        <div key={index} className="referral-item" style={{ animationDelay: `${0.3 + index * 0.05}s` }}>
                            <div className="referral-avatar">
                                {referral.name.charAt(0).toUpperCase()}
                            </div>
                            <div className="referral-details">
                                <div className="referral-name">{referral.name}</div>
                                <div className="referral-rank">{referral.rank}</div>
                            </div>
                            <div className="referral-bonus">+100</div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
