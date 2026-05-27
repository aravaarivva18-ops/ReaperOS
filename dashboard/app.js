/* app.js - ReaperOS Dashboard Logic with Live Telemetry Poll */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Uptime Clock
    let startTime = Date.now();
    const uptimeVal = document.getElementById('uptime-val');
    
    function updateUptime() {
        const diff = Date.now() - startTime;
        const hrs = String(Math.floor(diff / 3600000)).padStart(2, '0');
        const mins = String(Math.floor((diff % 3600000) / 60000)).padStart(2, '0');
        const secs = String(Math.floor((diff % 60000) / 1000)).padStart(2, '0');
        uptimeVal.textContent = `${hrs}:${mins}:${secs}`;
    }
    setInterval(updateUptime, 1000);

    // 2. Real-time Log Console & Simulator
    const consoleOutput = document.getElementById('console-output');
    const filterBtns = document.querySelectorAll('.filter-btn');
    let currentFilter = 'all';

    const logTemplates = [
        { level: 'info', text: 'Conductor: Инициализация сессии. Загружен профиль GEMINI_ANTIGRAVITY.md [L0 CORE]' },
        { level: 'debug', text: 'Conductor: Проверка версии Reaper OS... подтверждена v12.2 Frontier-Y' },
        { level: 'info', text: 'Conductor: Проверен лог-файл и внешняя память GLOBAL_CHRONICLE.md' },
        { level: 'info', text: 'Reaper: Начало сканирования проекта devtools... Найдено 15 файлов' },
        { level: 'debug', text: 'Reaper: Grep-поиск выявил дублирование функции copyToClipboard в tools/legal-gen.html' },
        { level: 'warn', text: 'Reaper: Обнаружено избыточное копирование CSS стилей в 3 файлах генераторов' },
        { level: 'info', text: 'Conductor: Создание плана имплементации refactoring_shared_assets.md' },
        { level: 'debug', text: 'Conductor: Получено подтверждение плана от пользователя (да).' },
        { level: 'info', text: 'Reaper: Создание файла shared.css с общими OLED-переменными' },
        { level: 'info', text: 'Reaper: Создание файла shared.js с Web Audio API кликами' },
        { level: 'debug', text: 'Reaper: Сургическое редактирование index.html. Удален дублированный CSS' },
        { level: 'debug', text: 'Reaper: Очищен скрипт в tools/nginx-gen.html, подключен shared.js' },
        { level: 'info', text: 'Ruflo: Запуск авто-верификации проекта через validate_assets.py' },
        { level: 'info', text: 'Ruflo: Проверка существования shared.css и shared.js... PASS' },
        { level: 'info', text: 'Ruflo: Проверка отсутствия локальных функций копирования... PASS' },
        { level: 'info', text: 'Ruflo: Все тесты завершены успешно. Ошибок не обнаружено.' },
        { level: 'debug', text: 'Conductor: Запись итогов работы в walkthrough.md' }
    ];

    let logHistory = [];

    function addLogLine(level, text) {
        const time = new Date().toLocaleTimeString();
        const logObj = { time, level, text };
        logHistory.push(logObj);
        
        // Render if matching filter
        if (currentFilter === 'all' || currentFilter === level) {
            renderLogLine(logObj);
        }
    }

    function renderLogLine(log) {
        const line = document.createElement('div');
        line.className = 'log-line';
        line.dataset.level = log.level;
        line.innerHTML = `
            <span class="log-time">[${log.time}]</span>
            <span class="log-level ${log.level}">${log.level.toUpperCase()}:</span>
            <span class="log-text">${log.text}</span>
        `;
        consoleOutput.appendChild(line);
        consoleOutput.scrollTop = consoleOutput.scrollHeight;
    }

    // Initialize with template logs sequentially
    let initIndex = 0;
    function loadInitialLogs() {
        if (initIndex < logTemplates.length) {
            const template = logTemplates[initIndex];
            addLogLine(template.level, template.text);
            initIndex++;
            setTimeout(loadInitialLogs, 400);
        } else {
            // Start live random logs generator
            setInterval(generateLiveLog, 5000);
        }
    }
    setTimeout(loadInitialLogs, 200);

    // Live log generator simulating background work
    const liveLogPool = [
        { level: 'debug', text: 'MemPalace: Запуск планового индексирования сессии в ChromaDB' },
        { level: 'info', text: 'Conductor: Завершен дрим-цикл. Обнаружено 0 новых уязвимостей в коде' },
        { level: 'info', text: 'Antigravity: Ожидание новых инструкций от пользователя...' },
        { level: 'debug', text: 'Ruflo: Мониторинг фоновых процессов... Daemon socket active' },
        { level: 'warn', text: 'Telemetry: Задержка API превысила 150ms при запросе к локальной LLM' },
        { level: 'info', text: 'Conductor: Синхронизация GLOBAL_CHRONICLE.md завершена' }
    ];

    function generateLiveLog() {
        const randLog = liveLogPool[Math.floor(Math.random() * liveLogPool.length)];
        addLogLine(randLog.level, randLog.text);
        
        // Trigger visual step activations
        triggerStepAnimation();
    }

    // Filter logs functionality
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            
            // Re-render logs
            consoleOutput.innerHTML = '';
            logHistory.forEach(log => {
                if (currentFilter === 'all' || currentFilter === log.level) {
                    renderLogLine(log);
                }
            });
        });
    });

    // 3. Telemetry Update logic (Dynamic API Polling)
    const latencyVal = document.getElementById('latency-val');
    const callsVal = document.getElementById('calls-val');
    const errorsVal = document.getElementById('errors-val');
    const chartBars = document.querySelectorAll('.chart-bar');
    
    const watchdogVal = document.getElementById('watchdog-val');
    const shieldVal = document.getElementById('shield-val');

    let totalCalls = 0;
    let totalErrors = 0;

    async function pollTelemetryData() {
        try {
            // Опрос телеметрии
            const resTelemetry = await fetch('http://localhost:5001/api/telemetry');
            if (resTelemetry.ok) {
                const dataObj = await resTelemetry.json();
                const telemetryRows = dataObj.data || [];
                
                if (telemetryRows.length > 0) {
                    // Последнее значение latency
                    const latestLatency = Math.round(telemetryRows[0].value);
                    latencyVal.textContent = `${latestLatency}ms`;
                    
                    if (latestLatency > 500) {
                        latencyVal.style.color = "var(--accent-cyan)"; // Warning color
                    } else {
                        latencyVal.style.color = "";
                    }
                    
                    // Обновляем шкалу графиков на основе последних значений
                    chartBars.forEach((bar, idx) => {
                        if (telemetryRows[idx]) {
                            const val = telemetryRows[idx].value;
                            // Пропорциональная высота (например, 1000ms = 100%)
                            const pct = Math.max(10, Math.min(100, (val / 1000) * 100));
                            bar.style.height = `${pct}%`;
                        }
                    });
                }
            }
            
            // Опрос статусов процессов
            const resStatus = await fetch('http://localhost:5001/api/status');
            if (resStatus.ok) {
                const dataObj = await resStatus.json();
                const statusList = dataObj.data || [];
                
                let isWatchdogHealthy = true;
                statusList.forEach(proc => {
                    if (proc.process_name === "embedder_server" && proc.is_alive === 0) {
                        isWatchdogHealthy = false;
                    }
                });
                
                if (isWatchdogHealthy) {
                    watchdogVal.textContent = "ACTIVE";
                    watchdogVal.className = "meta-value highlight-green";
                } else {
                    watchdogVal.textContent = "RECOVERING";
                    watchdogVal.className = "meta-value highlight-purple";
                }
            }
            
            shieldVal.textContent = "SECURE";
            shieldVal.className = "meta-value highlight-green";
            
            totalCalls++;
            callsVal.textContent = totalCalls;
            errorsVal.textContent = totalErrors;
            
        } catch (err) {
            // Если сервер API выключен
            latencyVal.textContent = "N/A";
            watchdogVal.textContent = "DOWN";
            watchdogVal.className = "meta-value highlight-purple"; // Red style
            
            shieldVal.textContent = "OFFLINE";
            shieldVal.className = "meta-value";
        }
    }

    // Запускаем опрос каждые 3 секунды
    setInterval(pollTelemetryData, 3000);
    pollTelemetryData();

    // 4. Trinity steps transitions
    const steps = [
        document.getElementById('conductor-step'),
        document.getElementById('reaper-step'),
        document.getElementById('ruflo-step')
    ];
    let activeStepIdx = 0;

    function triggerStepAnimation() {
        steps.forEach(s => s.classList.remove('active'));
        activeStepIdx = (activeStepIdx + 1) % steps.length;
        steps[activeStepIdx].classList.add('active');
    }

    // 5. Canvas Memory Vault Graph Visualization
    const canvas = document.getElementById('memory-canvas');
    const ctx = canvas.getContext('2d');
    
    // Fit canvas size
    function resizeCanvas() {
        if (!canvas.parentNode) return;
        const rect = canvas.parentNode.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Nodes generator
    const nodes = [];
    const numNodes = 15;
    for (let i = 0; i < numNodes; i++) {
        nodes.push({
            x: Math.random() * (canvas.width || 300),
            y: Math.random() * (canvas.height || 150),
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            radius: 3 + Math.random() * 4,
            color: Math.random() > 0.4 ? '#10b981' : '#8b5cf6'
        });
    }

    let mouseX = -9999;
    let mouseY = -9999;
    
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        mouseX = e.clientX - rect.left;
        mouseY = e.clientY - rect.top;
    });

    canvas.addEventListener('mouseleave', () => {
        mouseX = -9999;
        mouseY = -9999;
    });

    function drawGraph() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Update nodes physics
        nodes.forEach(node => {
            node.x += node.vx;
            node.y += node.vy;
            
            // Wall bounce
            if (node.x < 0 || node.x > canvas.width) node.vx *= -1;
            if (node.y < 0 || node.y > canvas.height) node.vy *= -1;

            // Interactive mouse attraction
            if (mouseX !== -9999) {
                const dx = mouseX - node.x;
                const dy = mouseY - node.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 80) {
                    node.x += (dx / dist) * 0.5;
                    node.y += (dy / dist) * 0.5;
                }
            }

            // Draw link lines
            nodes.forEach(other => {
                if (node === other) return;
                const dx = node.x - other.x;
                const dy = node.y - other.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 60) {
                    ctx.strokeStyle = `rgba(255, 255, 255, ${0.08 * (1 - dist / 60)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(node.x, node.y);
                    ctx.lineTo(other.x, other.y);
                    ctx.stroke();
                }
            });

            // Draw node circles
            ctx.fillStyle = node.color;
            ctx.shadowBlur = 8;
            ctx.shadowColor = node.color;
            ctx.beginPath();
            ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0; // Reset
        });
        
        requestAnimationFrame(drawGraph);
    }
    requestAnimationFrame(drawGraph);
});
