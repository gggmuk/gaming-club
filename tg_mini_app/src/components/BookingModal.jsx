import { useState } from 'react';
import { X, Calendar, Clock, Zap } from 'lucide-react';
import api, { getTelegramId } from '../lib/api';
import './BookingModal.css';

export default function BookingModal({ place, onClose, onSuccess }) {
    const [date, setDate] = useState('');
    const [startTime, setStartTime] = useState('');
    const [duration, setDuration] = useState(1);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            const telegramId = getTelegramId();
            const startDateTime = new Date(`${date}T${startTime}`);
            const endDateTime = new Date(startDateTime.getTime() + duration * 60 * 60 * 1000);

            await api.post('/create_booking/', {
                telegram_id: telegramId,
                place_id: place.id,
                start_time: startDateTime.toISOString(),
                end_time: endDateTime.toISOString(),
            });

            onSuccess?.();
        } catch (error) {
            console.error('Booking error:', error);
            alert(error.response?.data?.error || 'Ошибка при бронировании');
        } finally {
            setLoading(false);
        }
    };

    const getMinDate = () => new Date().toISOString().split('T')[0];

    const totalCost = place.tariff_info ? place.tariff_info.hourly_rate * duration : null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <div>
                        <h2>Забронировать</h2>
                        <p className="modal-subtitle">{place.name} • {place.place_type || 'Basic'}</p>
                    </div>
                    <button className="btn-close" onClick={onClose}>
                        <X size={22} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="booking-form">
                    <div className="form-group">
                        <label>
                            <Calendar size={16} />
                            Дата
                        </label>
                        <input
                            type="date"
                            className="input"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            min={getMinDate()}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>
                            <Clock size={16} />
                            Время начала
                        </label>
                        <input
                            type="time"
                            className="input"
                            value={startTime}
                            onChange={(e) => setStartTime(e.target.value)}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>
                            <Zap size={16} />
                            Длительность
                        </label>
                        <div className="duration-chips">
                            {[1, 2, 3, 4, 5, 6].map((h) => (
                                <button
                                    key={h}
                                    type="button"
                                    className={`dur-chip ${duration === h ? 'active' : ''}`}
                                    onClick={() => setDuration(h)}
                                >
                                    {h} {h === 1 ? 'час' : h < 5 ? 'часа' : 'часов'}
                                </button>
                            ))}
                        </div>
                    </div>

                    {totalCost !== null && (
                        <div className="price-info">
                            <div className="price-row">
                                <span>Тариф</span>
                                <span>{place.tariff_info.hourly_rate}₽ × {duration}ч</span>
                            </div>
                            <div className="price-total">
                                <span>Итого</span>
                                <strong>{totalCost}₽</strong>
                            </div>
                        </div>
                    )}

                    <button type="submit" className="btn" disabled={loading}>
                        {loading ? 'Бронирование...' : '📅 Забронировать'}
                    </button>
                </form>
            </div>
        </div>
    );
}
