"""
Script to fix the broken operations_dashboard.html JavaScript section.
This will rewrite the entire script block with correct structure.
"""

# Read the current file
with open(r'c:\codes\вкр\templates\operations_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find where the script tag starts
script_start = content.find('<script>')
if script_start == -1:
    print("ERROR: Could not find <script> tag")
    exit(1)

# Find where the script tag ends  
script_end = content.find('</script>', script_start)
if script_end == -1:
    print("ERROR: Could not find </script> tag")
    exit(1)

# Extract everything before and after the script section
before_script = content[:script_start + len('<script>')]
after_script = content[script_end:]

# Create the correct JavaScript content
js_content = """
                        // --- STATE & TABS ---
                        let currentTab = 'operational';
                        let clientsData = [];
                        window.allPlaces = [];

                        function switchTab(tab) {
                            document.querySelectorAll('nav button').forEach(btn => {
                                btn.classList.remove('tab-active');
                                btn.classList.add('tab-inactive');
                            });
                            document.getElementById(`tab-${tab}`).classList.remove('tab-inactive');
                            document.getElementById(`tab-${tab}`).classList.add('tab-active');

                            document.getElementById('view-operational').classList.add('hidden');
                            document.getElementById('view-analytics').classList.add('hidden');
                            document.getElementById('view-clients').classList.add('hidden');
                            document.getElementById('view-management').classList.add('hidden');

                            document.getElementById(`view-${tab}`).classList.remove('hidden');
                            currentTab = tab;

                            if (tab === 'operational') {
                                fetchPlaceStatus();
                                fetchTariffs();
                            }
                            if (tab === 'analytics') loadAnalytics();
                            if (tab === 'clients') loadClients();
                            if (tab === 'management') loadManagement();
                        }

                        // --- OPERATIONAL MODULE ---
                        async function fetchPlaceStatus() {
                            try {
                                const res = await fetch('/api/place_status/');
                                const places = await res.json();
                                window.allPlaces = places;
                                const grid = document.getElementById('places-grid');
                                grid.innerHTML = '';

                                places.forEach(place => {
                                    const isFree = place.status === 'free';
                                    const colorClass = isFree ? 'border-green-500/50 hover:shadow-green-500/20' : 'border-primary-500/50 hover:shadow-primary-500/20';
                                    const statusText = isFree ? '<span class="text-green-400">✓ Свободно</span>' : '<span class="text-primary-400">● Занято</span>';

                                    let actionBtn = '';
                                    if (isFree) {
                                        actionBtn = `<button onclick="openStartModal(${place.id})" class="w-full mt-3 py-1.5 rounded bg-green-600/20 text-green-400 text-xs font-medium border border-green-600/30 hover:bg-green-600/30 hover:scale-105 transition-all duration-200">✨ Начать</button>`;
                                    } else {
                                        actionBtn = `
                            <div class="flex space-x-2 mt-3">
                                <button onclick="openProlongModal(${place.active_session?.id})" class="flex-1 py-1.5 rounded bg-blue-600/20 text-blue-400 text-xs font-medium border border-blue-600/30 hover:bg-blue-600/30 hover:scale-105 transition-all">⏱️ Продлить</button>
                                <button onclick="stopSession(${place.active_session?.id})" class="flex-1 py-1.5 rounded bg-red-600/20 text-red-400 text-xs font-medium border border-red-600/30 hover:bg-red-600/30 hover:scale-105 transition-all">⏹️ Стоп</button>
                            </div>
                        `;
                                    }

                                    const card = document.createElement('div');
                                    card.className = `glass-panel place-card p-4 rounded-xl border shadow-lg ${colorClass}`;

                                    let tariffInfo = '';
                                    if (place.tariff_info) {
                                        tariffInfo = `<div class="text-[10px] text-gray-500 mt-1">${place.tariff_info.name} (${place.tariff_info.hourly_rate}₽/ч)</div>`;
                                    }

                                    let timeDisplay = '';
                                    if (!isFree && place.active_session) {
                                        if (place.active_session.scheduled_end_time) {
                                            const end = new Date(place.active_session.scheduled_end_time);
                                            const now = new Date();
                                            const diffMs = end - now;
                                            const diffMins = Math.ceil(diffMs / 60000);

                                            let timeText = '';
                                            let timeColor = 'text-white';

                                            if (diffMins > 0) {
                                                const h = Math.floor(diffMins / 60);
                                                const m = diffMins % 60;
                                                timeText = `${h > 0 ? h + 'ч ' : ''}${m}мин`;
                                                if (diffMins < 10) timeColor = 'text-red-400 animate-pulse';
                                            } else {
                                                timeText = 'Время вышло';
                                                timeColor = 'text-red-500 font-bold animate-pulse';
                                            }
                                            timeDisplay = `<div class="text-xs text-gray-400">⏳ <span class="${timeColor}">${timeText}</span></div>`;
                                        } else {
                                            timeDisplay = `<div class="text-xs text-gray-400">🕐 <span class="text-white">${new Date(place.active_session.start_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span></div>`;
                                        }
                                    } else {
                                        timeDisplay = '<div class="text-xs text-gray-500 h-8">Нет активной сессии</div>';
                                    }

                                    card.innerHTML = `
                        <div class="flex justify-between items-start mb-2">
                            <div>
                                <h3 class="font-bold text-white">${place.name}</h3>
                                ${tariffInfo}
                            </div>
                            <div class="text-xs">${statusText}</div>
                        </div>
                        ${!isFree && place.active_session ? `
                            <div class="text-xs text-gray-400 mb-1">👤 <span class="text-white">${place.client_name}</span></div>
                            ${timeDisplay}
                        ` : timeDisplay}
                        ${actionBtn}
                    `;

                                    card.addEventListener('click', (e) => {
                                        if (!e.target.closest('button')) fetchRecommendation(place.id);
                                    });

                                    grid.appendChild(card);
                                });
                            } catch (e) { console.error(e); }
                        }

                        async function fetchTariffs() {
                            try {
                                const res = await fetch('/api/tariffs/');
                                if (!res.ok) return;
                                const tariffs = await res.json();
                                const container = document.getElementById('tariffs-list');
                                container.innerHTML = '';

                                if (tariffs.length === 0) {
                                    container.innerHTML = '<div class="text-sm text-gray-400 text-center py-2">Нет активных тарифов</div>';
                                    return;
                                }

                                tariffs.forEach(t => {
                                    const div = document.createElement('div');
                                    div.className = 'bg-gray-800/50 rounded-lg p-3 border border-gray-700/50 flex justify-between items-center';
                                    div.innerHTML = `
                        <div>
                            <div class="text-sm font-medium text-white">${t.name}</div>
                            <div class="text-xs text-gray-400">${t.description || ''}</div>
                        </div>
                        <div class="text-sm font-bold text-primary-400">${t.hourly_rate}₽/ч</div>
                    `;
                                    container.appendChild(div);
                                });
                            } catch (e) { console.error("Failed to fetch tariffs", e); }
                        }

                        async function fetchRecommendation(placeId) {
                            try {
                                const res = await fetch(`/api/recommendations/${placeId}/`);
                                const data = await res.json();
                                document.getElementById('ai-insight').textContent = data.insight_text;

                                const priceEl = document.getElementById('ai-price-change');
                                const priceVal = document.getElementById('ai-price-val');
                                if (data.recommended_price_change !== '0%') {
                                    priceEl.classList.remove('hidden');
                                    priceVal.textContent = data.recommended_price_change;
                                    priceVal.className = data.recommended_price_change.includes('-') ? 'text-sm font-bold text-green-400' : 'text-sm font-bold text-red-400';
                                } else {
                                    priceEl.classList.add('hidden');
                                }
                            } catch (e) { console.error(e); }
                        }

                        // --- HELPERS ---
                        function getCookie(name) {
                            let cookieValue = null;
                            if (document.cookie && document.cookie !== '') {
                                const cookies = document.cookie.split(';');
                                for (let i = 0; i < cookies.length; i++) {
                                    const cookie = cookies[i].trim();
                                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                        break;
                                    }
                                }
                            }
                            return cookieValue;
                        }

                        // --- SESSION ACTIONS ---
                        async function openStartModal(placeId) {
                            document.getElementById('startPlaceId').value = placeId;
                            document.getElementById('startModal').classList.remove('hidden');

                            // Store rate for recalculation
                            const place = window.allPlaces ? window.allPlaces.find(p => p.id === placeId) : null;
                            const rate = (place && place.tariff_info) ? place.tariff_info.hourly_rate : 0;
                            document.getElementById('startModal').dataset.rate = rate;

                            // Fetch and populate promotions
                            try {
                                const res = await fetch('/api/promotions/');
                                const promotions = await res.json();
                                const select = document.getElementById('startPromotion');
                                if (select) {
                                    select.innerHTML = '<option value="" data-discount="0">Без акции</option>';
                                    promotions.forEach(p => {
                                        if (p.is_active) {
                                            select.innerHTML += `<option value="${p.id}" data-discount="${p.discount_percentage}">${p.name} (-${p.discount_percentage}%)</option>`;
                                        }
                                    });
                                    select.onchange = updateStartModalPrices;
                                }
                            } catch (e) { console.error("Failed to fetch promotions", e); }

                            // Initial price update
                            updateStartModalPrices();

                            // Reset form
                            document.getElementById('isGuestCheckbox').checked = false;
                            toggleGuestMode();
                            document.getElementById('startTelegramId').value = '';
                            document.getElementById('startClientName').value = '';

                            // Reset duration
                            selectDuration(0, document.querySelector('.duration-btn'));
                        }

                        function updateStartModalPrices() {
                            const rate = parseFloat(document.getElementById('startModal').dataset.rate || 0);
                            const select = document.getElementById('startPromotion');
                            const discount = select && select.selectedOptions[0] ? parseFloat(select.selectedOptions[0].dataset.discount || 0) : 0;

                            document.querySelectorAll('.duration-btn').forEach(btn => {
                                const mins = parseInt(btn.dataset.minutes);
                                let label = '';
                                const discountedRate = rate * (1 - discount / 100);

                                if (mins === 0) {
                                    label = `<span>Открытое</span><span class="text-[10px] opacity-70 mt-0.5">${Math.round(discountedRate)}₽/ч</span>`;
                                } else {
                                    const hours = mins / 60;
                                    const cost = hours * discountedRate;
                                    const hoursText = hours === 1 ? '1 час' : (hours < 5 ? `${hours} часа` : `${hours} часов`);
                                    label = `<span>${hoursText}</span><span class="text-[10px] opacity-70 mt-0.5">${Math.round(cost)}₽</span>`;
                                }
                                btn.innerHTML = label;
                            });
                        }

                        function selectDuration(minutes, btn) {
                            document.getElementById('startDuration').value = minutes;
                            document.querySelectorAll('.duration-btn').forEach(b => {
                                b.classList.remove('bg-primary-600', 'text-white', 'border-primary-500');
                                b.classList.add('bg-gray-700', 'text-gray-300', 'border-gray-600');
                            });
                            btn.classList.remove('bg-gray-700', 'text-gray-300', 'border-gray-600');
                            btn.classList.add('bg-primary-600', 'text-white', 'border-primary-500');
                        }

                        function toggleGuestMode() {
                            const isGuest = document.getElementById('isGuestCheckbox').checked;
                            const tgField = document.getElementById('telegramIdField');
                            const nameLabel = document.getElementById('nameLabel');
                            const nameInput = document.getElementById('startClientName');

                            if (isGuest) {
                                tgField.classList.add('hidden');
                                nameLabel.innerHTML = 'Имя гостя <span class="text-xs text-red-400">*</span>';
                                nameInput.placeholder = 'Введите имя гостя';
                            } else {
                                tgField.classList.remove('hidden');
                                nameLabel.innerHTML = 'Имя клиента <span class="text-xs text-gray-500">(для новых)</span>';
                                nameInput.placeholder = 'Иван Иванов';
                            }
                        }

                        async function submitStart() {
                            const placeId = document.getElementById('startPlaceId').value;
                            const telegramId = document.getElementById('startTelegramId').value;
                            const clientName = document.getElementById('startClientName').value.trim();
                            const isGuest = document.getElementById('isGuestCheckbox').checked;
                            const duration = document.getElementById('startDuration').value;
                            const promotionId = document.getElementById('startPromotion') ? document.getElementById('startPromotion').value : null;

                            if (!isGuest && !telegramId) {
                                alert('Введите Telegram ID клиента');
                                return;
                            }

                            if (isGuest && !clientName) {
                                alert('Введите имя гостя');
                                return;
                            }

                            try {
                                const payload = {
                                    place_id: placeId,
                                    is_guest: isGuest,
                                    duration: duration > 0 ? duration : null,
                                    promotion_id: promotionId || null
                                };

                                if (isGuest) {
                                    payload.guest_name = clientName;
                                } else {
                                    payload.telegram_id = telegramId;
                                    if (clientName) payload.client_name = clientName;
                                }

                                const res = await fetch('/api/start_session/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCookie('csrftoken')
                                    },
                                    body: JSON.stringify(payload)
                                });

                                if (res.ok) {
                                    closeModal('startModal');
                                    fetchPlaceStatus();
                                    alert('✅ Сессия начата!');
                                } else {
                                    const error = await res.json();
                                    alert('❌ Ошибка: ' + (error.error || error.detail || 'Неизвестная ошибка'));
                                }
                            } catch (e) {
                                console.error(e);
                                alert('❌ Ошибка соединения');
                            }
                        }

                        function openProlongModal(sessionId) {
                            if (!sessionId) return;
                            document.getElementById('prolongSessionId').value = sessionId;
                            document.getElementById('prolongModal').classList.remove('hidden');
                        }

                        function closeModal(id) {
                            document.getElementById(id).classList.add('hidden');
                        }

                        function setProlongTime(min) {
                            document.getElementById('prolongMinutes').value = min;
                        }

                        async function submitProlong() {
                            const id = document.getElementById('prolongSessionId').value;
                            const min = document.getElementById('prolongMinutes').value;
                            try {
                                const res = await fetch('/api/prolong_session/', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                        'X-CSRFToken': getCookie('csrftoken')
                                    },
                                    body: JSON.stringify({ session_id: id, minutes_to_add: min })
                                });
                                if (res.ok) {
                                    closeModal('prolongModal');
                                    fetchPlaceStatus();
                                    alert('✅ Сессия продлена!');
                                } else {
                                    const error = await res.json();
                                    alert('❌ Ошибка: ' + (error.error || error.detail || 'Ошибка продления'));
                                }
                            } catch (e) { console.error(e); }
                        }

                        async function stopSession(sessionId) {
                            if (!confirm('⏹️ Завершить сессию?')) return;
                            try {
                                const res = await fetch(`/api/stop_session/${sessionId}/`, {
                                    method: 'POST',
                                    headers: {
                                        'X-CSRFToken': getCookie('csrftoken')
                                    }
                                });
                                if (res.ok) {
                                    fetchPlaceStatus();
                                    alert('✅ Сессия завершена!');
                                } else {
                                    const error = await res.json();
                                    alert('❌ Ошибка: ' + (error.error || error.detail || 'Ошибка завершения'));
                                }
                            } catch (e) { console.error(e); }
                        }

                        // --- ANALYTICS MODULE ---
                        let chartInstance = null;
                        async function loadAnalytics() {
                            try {
                                const res = await fetch('/api/manager_stats/');
                                if (!res.ok) throw new Error('Failed to load stats');
                                const data = await res.json();

                                document.getElementById('kpi-revenue').textContent = Math.round(data.total_revenue_day || 0).toLocaleString();
                                document.getElementById('kpi-occupancy').textContent = data.occupancy_rate_current || 0;
                                document.getElementById('kpi-avg-check').textContent = Math.round(data.avg_session_cost || 0);
                                document.getElementById('kpi-top-place').textContent = data.top_performing_place_name || 'N/A';

                                renderChart();
                            } catch (e) { console.error("Analytics Error:", e); }
                        }

                        function renderChart() {
                            const ctx = document.getElementById('revenueChart').getContext('2d');
                            if (chartInstance) chartInstance.destroy();

                            const labels = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
                            const data = [12000, 19000, 15000, 22000, 28000, 35000, 31000];

                            chartInstance = new Chart(ctx, {
                                type: 'line',
                                data: {
                                    labels: labels,
                                    datasets: [{
                                        label: 'Выручка',
                                        data: data,
                                        borderColor: '#6366f1',
                                        backgroundColor: 'rgba(99, 102, 241, 0.1)',
                                        borderWidth: 3,
                                        fill: true,
                                        tension: 0.4
                                    }]
                                },
                                options: {
                                    responsive: true,
                                    maintainAspectRatio: false,
                                    plugins: { legend: { display: false } },
                                    scales: {
                                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                                        x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
                                    }
                                }
                            });
                        }

                        // --- CLIENTS MODULE ---
                        async function loadClients() {
                            try {
                                const res = await fetch('/api/clients/');
                                clientsData = await res.json();
                                renderClients(clientsData);
                            } catch (e) { console.error(e); }
                        }

                        function renderClients(clients) {
                            const tbody = document.getElementById('clients-table-body');
                            tbody.innerHTML = '';
                            clients.forEach(client => {
                                const tr = document.createElement('tr');
                                tr.className = 'bg-gray-800/30 border-b border-gray-700 hover:bg-gray-700/50 transition-all hover:scale-[1.01]';
                                tr.innerHTML = `
                    <td class="px-6 py-4 font-medium text-white">${client.id}</td>
                    <td class="px-6 py-4">${client.name}</td>
                    <td class="px-6 py-4"><span class="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">${client.rank}</span></td>
                    <td class="px-6 py-4 text-accent-400 font-bold">${client.bonus_points}</td>
                    <td class="px-6 py-4">${client.total_hours_played}</td>
                `;
                                tbody.appendChild(tr);
                            });
                        }

                        document.getElementById('client-search').addEventListener('input', (e) => {
                            const term = e.target.value.toLowerCase();
                            const filtered = clientsData.filter(c =>
                                c.name.toLowerCase().includes(term) ||
                                String(c.id).includes(term) ||
                                String(c.telegram_id).includes(term)
                            );
                            renderClients(filtered);
                        });

                        // --- MANAGEMENT MODULE ---
                        async function loadManagement() {
                            try {
                                // Fetch Tariffs
                                const resT = await fetch('/api/tariffs/');
                                const tariffs = await resT.json();
                                renderTariffsManagement(tariffs);

                                // Fetch Promotions
                                const resP = await fetch('/api/promotions/');
                                const promotions = await resP.json();
                                renderPromotionsManagement(promotions);
                            } catch (e) { console.error(e); }
                        }

                        function renderTariffsManagement(tariffs) {
                            const container = document.getElementById('manage-tariffs-list');
                            container.innerHTML = '';
                            tariffs.forEach(t => {
                                const div = document.createElement('div');
                                div.className = 'bg-gray-800/50 rounded-lg p-4 border border-gray-700/50 flex justify-between items-center';
                                div.innerHTML = `
                    <div>
                        <div class="font-bold text-white">${t.name}</div>
                        <div class="text-sm text-primary-400">${t.hourly_rate}₽/ч</div>
                        <div class="text-xs text-gray-400 mt-1">${t.description || ''}</div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick='openTariffModal(${JSON.stringify(t)})' class="p-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300">✏️</button>
                        <button onclick="deleteTariff(${t.id})" class="p-2 bg-red-900/30 hover:bg-red-900/50 border border-red-900/50 rounded text-red-400">🗑️</button>
                    </div>
                `;
                                container.appendChild(div);
                            });
                        }

                        function renderPromotionsManagement(promotions) {
                            const container = document.getElementById('manage-promotions-list');
                            container.innerHTML = '';
                            promotions.forEach(p => {
                                const div = document.createElement('div');
                                div.className = 'bg-gray-800/50 rounded-lg p-4 border border-gray-700/50 flex justify-between items-center';
                                const statusBadge = p.is_active ? '<span class="px-2 py-1 bg-green-900/30 text-green-400 rounded text-xs">Активна</span>' : '<span class="px-2 py-1 bg-gray-700 text-gray-400 rounded text-xs">Неактивна</span>';
                                div.innerHTML = `
                    <div>
                        <div class="font-bold text-white">${p.name}</div>
                        <div class="text-sm text-accent-400">-${p.discount_percentage}%</div>
                        <div class="text-xs text-gray-400 mt-1">${p.description || ''}</div>
                        <div class="mt-2">${statusBadge}</div>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick='openPromotionModal(${JSON.stringify(p)})' class="p-2 bg-gray-700 hover:bg-gray-600 rounded text-gray-300">✏️</button>
                        <button onclick="deletePromotion(${p.id})" class="p-2 bg-red-900/30 hover:bg-red-900/50 border border-red-900/50 rounded text-red-400">🗑️</button>
                    </div>
                `;
                                container.appendChild(div);
                            });
                        }

                        // Tariff Actions
                        function openTariffModal(tariff = null) {
                            document.getElementById('tariffModal').classList.remove('hidden');
                            if (tariff) {
                                document.getElementById('tariffModalTitle').textContent = 'Редактировать Тариф';
                                document.getElementById('tariffId').value = tariff.id;
                                document.getElementById('tariffName').value = tariff.name;
                                document.getElementById('tariffRate').value = tariff.hourly_rate;
                                document.getElementById('tariffDesc').value = tariff.description;
                                document.getElementById('tariffActive').checked = tariff.is_active;
                            } else {
                                document.getElementById('tariffModalTitle').textContent = 'Добавить Тариф';
                                document.getElementById('tariffId').value = '';
                                document.getElementById('tariffName').value = '';
                                document.getElementById('tariffRate').value = '';
                                document.getElementById('tariffDesc').value = '';
                                document.getElementById('tariffActive').checked = true;
                            }
                        }

                        async function submitTariff() {
                            const id = document.getElementById('tariffId').value;
                            const data = {
                                name: document.getElementById('tariffName').value,
                                hourly_rate: document.getElementById('tariffRate').value,
                                description: document.getElementById('tariffDesc').value,
                                is_active: document.getElementById('tariffActive').checked
                            };

                            const url = id ? `/api/tariffs/${id}/` : '/api/tariffs/manage/';
                            const method = id ? 'PUT' : 'POST';

                            try {
                                const res = await fetch(url, {
                                    method: method,
                                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                                    body: JSON.stringify(data)
                                });
                                if (res.ok) {
                                    closeModal('tariffModal');
                                    loadManagement();
                                    if (currentTab === 'operational') fetchTariffs(); // Refresh sidebar if needed
                                } else {
                                    alert('Ошибка сохранения');
                                }
                            } catch (e) { console.error(e); }
                        }

                        async function deleteTariff(id) {
                            if (!confirm('Удалить тариф?')) return;
                            try {
                                const res = await fetch(`/api/tariffs/${id}/`, {
                                    method: 'DELETE',
                                    headers: { 'X-CSRFToken': getCookie('csrftoken') }
                                });
                                if (res.ok) loadManagement();
                            } catch (e) { console.error(e); }
                        }

                        // Promotion Actions
                        function openPromotionModal(promo = null) {
                            document.getElementById('promotionModal').classList.remove('hidden');
                            if (promo) {
                                document.getElementById('promotionModalTitle').textContent = 'Редактировать Акцию';
                                document.getElementById('promotionId').value = promo.id;
                                document.getElementById('promotionName').value = promo.name;
                                document.getElementById('promotionDiscount').value = promo.discount_percentage;
                                document.getElementById('promotionDesc').value = promo.description;
                                document.getElementById('promotionActive').checked = promo.is_active;
                            } else {
                                document.getElementById('promotionModalTitle').textContent = 'Добавить Акцию';
                                document.getElementById('promotionId').value = '';
                                document.getElementById('promotionName').value = '';
                                document.getElementById('promotionDiscount').value = '';
                                document.getElementById('promotionDesc').value = '';
                                document.getElementById('promotionActive').checked = true;
                            }
                        }

                        async function submitPromotion() {
                            const id = document.getElementById('promotionId').value;
                            const data = {
                                name: document.getElementById('promotionName').value,
                                discount_percentage: document.getElementById('promotionDiscount').value,
                                description: document.getElementById('promotionDesc').value,
                                is_active: document.getElementById('promotionActive').checked
                            };

                            const url = id ? `/api/promotions/${id}/` : '/api/promotions/';
                            const method = id ? 'PUT' : 'POST';

                            try {
                                const res = await fetch(url, {
                                    method: method,
                                    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCookie('csrftoken') },
                                    body: JSON.stringify(data)
                                });
                                if (res.ok) {
                                    closeModal('promotionModal');
                                    loadManagement();
                                } else {
                                    alert('Ошибка сохранения');
                                }
                            } catch (e) { console.error(e); }
                        }

                        async function deletePromotion(id) {
                            if (!confirm('Удалить акцию?')) return;
                            try {
                                const res = await fetch(`/api/promotions/${id}/`, {
                                    method: 'DELETE',
                                    headers: { 'X-CSRFToken': getCookie('csrftoken') }
                                });
                                if (res.ok) loadManagement();
                            } catch (e) { console.error(e); }
                        }

                        // Init
                        document.addEventListener('DOMContentLoaded', () => {
                            fetchPlaceStatus();
                            fetchTariffs();
                            setInterval(() => {
                                if (currentTab === 'operational') fetchPlaceStatus();
                            }, 30000);
                        });
                    """

# Combine all parts
fixed_content = before_script + js_content + after_script

# Write the fixed content back
with open(r'c:\codes\вкр\templates\operations_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Fixed operations_dashboard.html JavaScript section!")
print("The script block has been completely rewritten with correct structure.")
