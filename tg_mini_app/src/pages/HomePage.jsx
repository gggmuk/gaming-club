import { useState, useEffect } from 'react';
import { Monitor, Wifi, Coffee } from 'lucide-react';
import api from '../lib/api';
import BookingModal from '../components/BookingModal';
import './HomePage.css';

export default function HomePage() {
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [selectedPlace, setSelectedPlace] = useState(null);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        loadPlaces();
        const interval = setInterval(loadPlaces, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadPlaces = async () => {
        try {
            const response = await api.get('/place_status/');
            setPlaces(response.data);
        } catch (error) {
            console.error('Error loading places:', error);
        } finally {
            setLoading(false);
        }
    };

    const getPlaceIcon = (type) => {
        switch (type) {
            case 'VIP': return <Wifi className="place-icon vip" />;
            case 'Bootcamp': return <Coffee className="place-icon bootcamp" />;
            default: return <Monitor className="place-icon basic" />;
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'free': return '#10b981';
            case 'occupied': return '#ef4444';
            default: return '#f59e0b';
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'free': return 'Свободно';
            case 'occupied': return 'Занято';
            default: return 'Обслуживание';
        }
    };

    const getTimeDisplay = (place) => {
        if (place.status !== 'occupied' || !place.active_session) return null;
        if (place.active_session.scheduled_end_time) {
            const end = new Date(place.active_session.scheduled_end_time);
            const diff = Math.ceil((end - new Date()) / 60000);
            if (diff > 0) {
                const h = Math.floor(diff / 60), m = diff % 60;
                return <div className="place-time">⏳ {h > 0 ? `${h}ч ` : ''}{m}мин</div>;
            }
            return <div className="place-time" style={{ color: '#ef4444' }}>⏰ Время вышло</div>;
        }
        const start = new Date(place.active_session.start_time);
        return <div className="place-time">🕐 с {start.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</div>;
    };

    const filteredPlaces = filter === 'all'
        ? places
        : filter === 'free'
            ? places.filter(p => p.status === 'free')
            : places.filter(p => p.place_type === filter);

    const freeCount = places.filter(p => p.status === 'free').length;
    const occupiedCount = places.filter(p => p.status === 'occupied').length;

    if (loading) {
        return <div className="container"><div className="loading">Загрузка мест...</div></div>;
    }

    return (
        <div className="container home-page">
            <h1 className="page-title">🎮 Игровые места</h1>

            {/* Status Summary */}
            <div className="status-summary">
                <div className="summary-chip">
                    <span className="dot green"></span>
                    <span>{freeCount} свободно</span>
                </div>
                <div className="summary-chip">
                    <span className="dot red"></span>
                    <span>{occupiedCount} занято</span>
                </div>
                <div className="summary-chip">
                    <span className="dot amber"></span>
                    <span>{places.length} всего</span>
                </div>
            </div>

            {/* Filter Tabs */}
            <div className="filter-tabs">
                {['all', 'free', 'VIP', 'Basic', 'Bootcamp'].map(f => (
                    <button
                        key={f}
                        className={`filter-tab ${filter === f ? 'active' : ''}`}
                        onClick={() => setFilter(f)}
                    >
                        {f === 'all' ? 'Все' : f === 'free' ? '✓ Свободные' : f}
                    </button>
                ))}
            </div>

            <div className="places-grid">
                {filteredPlaces.map((place, index) => (
                    <div 
                        key={place.id} 
                        className={`place-card ${place.status} animate-fade-in`}
                        style={{ animationDelay: `${index * 0.05}s` }}
                    >
                        <div className="place-header">
                            {getPlaceIcon(place.place_type)}
                            <div>
                                <h3>{place.name}</h3>
                                <span className="place-type">{place.place_type || 'Basic'}</span>
                            </div>
                        </div>
                        
                        <div className="place-status">
                            <div className="status-indicator" style={{ backgroundColor: getStatusColor(place.status) }} />
                            <span>{getStatusText(place.status)}</span>
                        </div>

                        {place.status === 'occupied' && place.client_name && (
                            <div className="place-client">👤 {place.client_name}</div>
                        )}

                        {place.tariff_info && (
                            <>
                                <div className="place-tariff-name">{place.tariff_info.name}</div>
                                <div className="place-price">{place.tariff_info.hourly_rate}₽/час</div>
                            </>
                        )}

                        {getTimeDisplay(place)}

                        {place.status === 'free' && (
                            <button className="btn btn-book" onClick={() => setSelectedPlace(place)}>
                                📅 Забронировать
                            </button>
                        )}
                    </div>
                ))}
            </div>

            {filteredPlaces.length === 0 && (
                <div className="empty-state">
                    <p>Нет мест по выбранному фильтру</p>
                </div>
            )}

            {selectedPlace && (
                <BookingModal
                    place={selectedPlace}
                    onClose={() => setSelectedPlace(null)}
                    onSuccess={() => {
                        loadPlaces();
                        setSelectedPlace(null);
                    }}
                />
            )}
        </div>
    );
}
