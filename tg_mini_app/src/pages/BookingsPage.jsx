import { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, AlertCircle } from 'lucide-react';
import api, { getTelegramId } from '../lib/api';
import './BookingsPage.css';

export default function BookingsPage() {
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => { loadBookings(); }, []);

    const loadBookings = async () => {
        try {
            const telegramId = getTelegramId();
            const response = await api.get(`/my_bookings/${telegramId}/`);
            setBookings(response.data);
        } catch (error) {
            console.error('Error loading bookings:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCancelBooking = async (bookingId) => {
        if (!confirm('Отменить бронирование?')) return;
        try {
            await api.patch(`/cancel_booking/${bookingId}/`, { status: 'canceled' });
            loadBookings();
        } catch (error) {
            console.error('Error canceling booking:', error);
        }
    };

    const statusConfig = {
        pending: { text: 'Ожидает', color: '#f59e0b', icon: '⏳' },
        confirmed: { text: 'Подтверждено', color: '#10b981', icon: '✅' },
        canceled: { text: 'Отменено', color: '#ef4444', icon: '❌' },
        completed: { text: 'Завершено', color: '#64748b', icon: '✔️' },
    };

    const formatDateTime = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleString('ru-RU', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
    };

    const getDuration = (start, end) => {
        const diff = (new Date(end) - new Date(start)) / 3600000;
        return diff < 1 ? `${Math.round(diff * 60)}мин` : `${diff.toFixed(0)}ч`;
    };

    const filtered = filter === 'all' ? bookings : bookings.filter(b => b.status === filter);
    const activeCount = bookings.filter(b => ['pending', 'confirmed'].includes(b.status)).length;

    if (loading) return <div className="container"><div className="loading">Загрузка броней...</div></div>;

    return (
        <div className="container bookings-page">
            <h1 className="page-title">📅 Мои бронирования</h1>

            {/* Summary */}
            {bookings.length > 0 && (
                <div className="bookings-summary animate-fade-in">
                    <div className="summary-stat">
                        <span className="summary-num">{bookings.length}</span>
                        <span className="summary-txt">всего</span>
                    </div>
                    <div className="summary-divider"></div>
                    <div className="summary-stat">
                        <span className="summary-num" style={{ color: '#10b981' }}>{activeCount}</span>
                        <span className="summary-txt">активных</span>
                    </div>
                </div>
            )}

            {/* Filter */}
            {bookings.length > 0 && (
                <div className="filter-tabs" style={{ marginBottom: 20 }}>
                    {[['all', 'Все'], ['pending', '⏳ Ожидает'], ['confirmed', '✅ Подтв.'], ['canceled', '❌ Отмен.']].map(([val, label]) => (
                        <button key={val} className={`filter-tab ${filter === val ? 'active' : ''}`} onClick={() => setFilter(val)}>
                            {label}
                        </button>
                    ))}
                </div>
            )}

            {filtered.length === 0 ? (
                <div className="empty-state animate-fade-in">
                    <Calendar size={48} />
                    <p style={{ fontWeight: 600, fontSize: 16 }}>{bookings.length === 0 ? 'У вас пока нет броней' : 'Нет броней по фильтру'}</p>
                    <p className="hint">Забронируйте место на главной странице</p>
                </div>
            ) : (
                <div className="bookings-list">
                    {filtered.map((booking, idx) => {
                        const cfg = statusConfig[booking.status] || statusConfig.pending;
                        return (
                            <div key={booking.id} className="booking-card animate-fade-in" style={{ animationDelay: `${idx * 0.05}s` }}>
                                <div className="booking-header">
                                    <div className="booking-place">
                                        <MapPin size={18} style={{ color: 'var(--primary-light)', flexShrink: 0 }} />
                                        <h3>{booking.place_name}</h3>
                                    </div>
                                    <span className="status-badge" style={{ backgroundColor: cfg.color }}>
                                        {cfg.icon} {cfg.text}
                                    </span>
                                </div>

                                <div className="booking-details">
                                    <div className="detail-row">
                                        <Clock size={14} />
                                        <span>{formatDateTime(booking.start_time)} → {formatDateTime(booking.end_time)}</span>
                                    </div>
                                    <div className="detail-row">
                                        <AlertCircle size={14} />
                                        <span>Длительность: {getDuration(booking.start_time, booking.end_time)}</span>
                                    </div>
                                </div>

                                {(booking.status === 'pending' || booking.status === 'confirmed') && (
                                    <button className="btn btn-cancel" onClick={() => handleCancelBooking(booking.id)}>
                                        Отменить бронь
                                    </button>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
