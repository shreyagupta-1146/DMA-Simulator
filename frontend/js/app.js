// ========================================
// DMA CONTROLLER SIMULATOR - MAIN APP
// Core application logic, WebSocket, Charts
// ========================================
// GLOBAL SOCKET REFERENCE - FIXES SCOPE ISSUE
window.globalSocket = null;
// Global State
let socket;
let charts = {};
let simulationActive = false;
let currentOS = 'windows';
let currentMode = 'cpu';
let systemProfiles = {};
let currentFileInfo = null;

// Chart data storage
const chartDataLength = 100;
const chartData = {
    cpu: Array(chartDataLength).fill(0),
    dma: Array(chartDataLength).fill(0),
    bus: Array(chartDataLength).fill(0),
    throughput: Array(chartDataLength).fill(0)
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    initializeCharts();
    initializeEventListeners();
    loadSystemInfo();
    setupSystemProfiles();
});

/**
 * WebSocket Connection
 */
function initializeWebSocket() {
    const socket = io({
        transports: ['websocket', 'polling'],
        path: '/socket.io/'  // Explicit path for Socket.IO
    });

    window.globalSocket = socket;  // CRITICAL: Make socket globally accessible

    socket.on('connect', () => {
        console.log('✅ Connected to DMA Controller Simulator');
        addLogEntry('Connected to DMA Controller Simulator server', 'success');
        updateStatus('IDLE', 'idle');
        document.getElementById('system-status-text').textContent = 'CONNECTED';
    });

    socket.on('disconnect', () => {
        console.log('⚠️ Disconnected from server');
        addLogEntry('Disconnected from server. Please restart the application.', 'error');
        updateStatus('DISCONNECTED', 'idle');
        document.getElementById('system-status-text').textContent = 'DISCONNECTED';
    });

    socket.on('connection_response', (data) => {
        console.log('Connection response:', data);
    });

    socket.on('system_info', (data) => {
        console.log('System info received:', data);
        updateSystemInfoUI(data.profile);
    });

    socket.on('simulation_started', (data) => {
        console.log('Simulation started:', data);
        simulationActive = true;
        updateStatus('RUNNING', 'active');
        document.getElementById('start-transfer').disabled = true;
        document.getElementById('pause-transfer').disabled = false;
        document.getElementById('stop-transfer').disabled = false;
        addLogEntry(`Simulation started in ${data.mode.toUpperCase()} mode`, 'info');
    });

    socket.on('simulation_update', (data) => {
        updateMetrics(data);
    });

    socket.on('simulation_complete', (data) => {
        handleSimulationComplete(data);
    });

    socket.on('simulation_paused', () => {
        simulationActive = false;
        document.getElementById('system-status-text').textContent = 'PAUSED';
        addLogEntry('Simulation paused', 'warning');
    });

    socket.on('simulation_resumed', () => {
        simulationActive = true;
        document.getElementById('system-status-text').textContent = 'RUNNING';
        addLogEntry('Simulation resumed', 'info');
    });

    socket.on('simulation_stopped', () => {
        handleSimulationStop();
    });

    socket.on('simulation_error', (data) => {
        addLogEntry(`Simulation error: ${data.message}`, 'error');
        handleSimulationStop();
    });

    socket.on('analytics_report', (report) => {
        displayAnalyticsReport(report);
    });

    socket.on('analytics_error', (data) => {
        addLogEntry(`Analytics error: ${data.message}`, 'warning');
    });
}

/**
 * Initialize Chart.js Charts
 */
function initializeCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 0
        },
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                enabled: true,
                backgroundColor: 'rgba(30, 41, 59, 0.9)',
                titleColor: '#f1f5f9',
                bodyColor: '#cbd5e1',
                borderColor: '#334155',
                borderWidth: 1,
                padding: 12,
                displayColors: false
            }
        },
        scales: {
            x: {
                display: false
            },
            y: {
                min: 0,
                max: 100,
                ticks: {
                    color: '#94a3b8',
                    font: {
                        family: 'JetBrains Mono',
                        size: 10
                    }
                },
                grid: {
                    color: 'rgba(51, 65, 85, 0.5)'
                }
            }
        },
        interaction: {
            intersect: false,
            mode: 'index'
        }
    };

    // CPU Utilization Chart
    charts.cpu = new Chart(document.getElementById('cpu-chart'), {
        type: 'line',
        data: {
            labels: Array(chartDataLength).fill(''),
            datasets: [{
                label: 'CPU Utilization',
                data: chartData.cpu,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#2563eb',
                pointHoverBorderColor: '#f1f5f9',
                pointHoverBorderWidth: 2
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        title: function () {
                            return 'CPU Utilization & Cycles';
                        },
                        label: function (context) {
                            const cycles = context.parsed.y * 10000;
                            return [
                                `Utilization: ${context.parsed.y.toFixed(2)}%`,
                                `Estimated CPU Cycles: ${Math.round(cycles).toLocaleString()}`
                            ];
                        }
                    }
                }
            }
        }
    });

    // DMA Utilization Chart
    charts.dma = new Chart(document.getElementById('dma-chart'), {
        type: 'line',
        data: {
            labels: Array(chartDataLength).fill(''),
            datasets: [{
                label: 'DMA Utilization',
                data: chartData.dma,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#10b981',
                pointHoverBorderColor: '#f1f5f9'
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        title: function () {
                            return 'DMA Utilization';
                        },
                        label: function (context) {
                            const activeChannels = Math.round(context.parsed.y / 25);
                            return [
                                `Utilization: ${context.parsed.y.toFixed(2)}%`,
                                `Active Channels: ${activeChannels}/4`
                            ];
                        }
                    }
                }
            }
        }
    });

    // Bus Utilization Chart
    charts.bus = new Chart(document.getElementById('bus-chart'), {
        type: 'line',
        data: {
            labels: Array(chartDataLength).fill(''),
            datasets: [{
                label: 'Bus Utilization',
                data: chartData.bus,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#8b5cf6',
                pointHoverBorderColor: '#f1f5f9'
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        title: function () {
                            return 'Bus Utilization';
                        },
                        label: function (context) {
                            const bandwidth = context.parsed.y * 2;
                            return [
                                `Utilization: ${context.parsed.y.toFixed(2)}%`,
                                `Bandwidth: ${bandwidth.toFixed(2)} MB/s`
                            ];
                        }
                    }
                }
            }
        }
    });

    // Throughput Chart
    const throughputOptions = { ...commonOptions };
    throughputOptions.scales.y.max = 250;
    charts.throughput = new Chart(document.getElementById('throughput-chart'), {
        type: 'line',
        data: {
            labels: Array(chartDataLength).fill(''),
            datasets: [{
                label: 'Throughput',
                data: chartData.throughput,
                borderColor: '#f59e0b',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6,
                pointHoverBackgroundColor: '#f59e0b',
                pointHoverBorderColor: '#f1f5f9'
            }]
        },
        options: {
            ...throughputOptions,
            plugins: {
                ...commonOptions.plugins,
                tooltip: {
                    ...commonOptions.plugins.tooltip,
                    callbacks: {
                        title: function () {
                            return 'Transfer Throughput';
                        },
                        label: function (context) {
                            return `Speed: ${context.parsed.y.toFixed(2)} MB/s`;
                        }
                    }
                }
            }
        }
    });

    // Comparison Chart (CPU vs DMA)
    charts.comparison = new Chart(document.getElementById('comparison-chart'), {
        type: 'bar',
        data: {
            labels: ['CPU Only Mode', 'DMA Assisted Mode'],
            datasets: [{
                label: 'Efficiency (%)',
                data: [40, 95],
                backgroundColor: [
                    'rgba(239, 68, 68, 0.6)',
                    'rgba(16, 185, 129, 0.6)'
                ],
                borderColor: [
                    '#ef4444',
                    '#10b981'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    enabled: true,
                    backgroundColor: 'rgba(30, 41, 59, 0.9)',
                    titleColor: '#f1f5f9',
                    bodyColor: '#cbd5e1',
                    callbacks: {
                        title: function () {
                            return 'Performance Comparison';
                        },
                        label: function (context) {
                            const mode = context.label;
                            const efficiency = context.parsed.y;
                            const description = mode.includes('CPU')
                                ? 'High CPU overhead, slower transfers'
                                : 'Low CPU overhead, faster transfers';
                            return [
                                `${mode}: ${efficiency}% efficiency`,
                                description
                            ];
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        color: '#94a3b8',
                        font: {
                            family: 'JetBrains Mono',
                            size: 10
                        }
                    },
                    grid: {
                        color: 'rgba(51, 65, 85, 0.5)'
                    }
                },
                x: {
                    ticks: {
                        color: '#cbd5e1',
                        font: {
                            family: 'Inter',
                            size: 11
                        }
                    },
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize Event Listeners
 */
function initializeEventListeners() {
    // OS Selection
    document.querySelectorAll('.os-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.os-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            currentOS = card.dataset.os;
            switchOS(currentOS);

            // Log detailed OS specs
            const profile = systemProfiles[currentOS];
            addLogEntry(``, 'info'); // Spacer
            addLogEntry(`🖥️ SWITCHED TO: ${profile.name.toUpperCase()}`, 'info');
            addLogEntry(`   Scheduler: ${profile.scheduler_type}`, 'info');
            addLogEntry(`   Bandwidth: ${profile.max_dma_bandwidth} MB/s`, 'info');
            addLogEntry(`   Context Switch: ${profile.context_switch_overhead} cycles`, 'info');
            addLogEntry(`   CPU Cores: ${profile.cpu_cores}`, 'info');
            addLogEntry(`   Clock Speed: ${profile.clock_speed_ghz} GHz`, 'info');
            addLogEntry(`   DMA Priority: ${profile.dma_priority.toUpperCase()}`, 'info');
            addLogEntry(`   ${profile.description}`, 'info');
            addLogEntry(``, 'info'); // Spacer
        });
    });

    // Mode Selection
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            const modeName = btn.querySelector('span:first-child').textContent;
            addLogEntry(`Transfer mode set to: ${modeName} (${currentMode.toUpperCase()})`, 'info');

            // Update mode badge in transfer section
            const modeBadge = document.getElementById('current-mode-badge');
            modeBadge.innerHTML = `
                <i class="fas ${currentMode === 'cpu' ? 'fa-microchip' : 'fa-bolt'}"></i>
                <span>${currentMode.toUpperCase()}</span>
            `;
        });
    });

    // START BUTTON - FIXED WITH GLOBAL SOCKET AND CORRECT DOM ELEMENTS
    document.getElementById('start-transfer').addEventListener('click', () => {
        console.log('🚀 START BUTTON CLICKED - Using globalSocket');

        if (!window.globalSocket || !window.globalSocket.connected) {
            console.error('❌ Socket not connected!');
            addLogEntry('❌ Socket disconnected. Refresh page.', 'error');
            return;
        }

        // Check if file is uploaded
        const fileInfo = window.fileUpload ? window.fileUpload.getFileInfo() : null;
        if (!fileInfo) {
            addLogEntry('⚠️ Please upload a file first!', 'warning');
            return;
        }

        const fileSizeBytes = fileInfo.size_bytes;
        const fileType = fileInfo.file_type || 'text';
        const simSpeed = 1.0; // Default speed since sim-speed input is missing

        console.log('📤 Emitting start_transfer event...');

        window.globalSocket.emit('start_transfer', {
            file_size: fileSizeBytes,
            file_type: fileType,
            mode: currentMode,
            simulation_speed: simSpeed
        });

        console.log('✅ Event emitted successfully!');
        addLogEntry('📤 Simulation started!', 'info');

        // Update UI
        document.getElementById('start-transfer').disabled = true;
        document.getElementById('system-status-text').textContent = 'RUNNING';
    });

    // Pause/Resume Transfer Button
    document.getElementById('pause-transfer').addEventListener('click', () => {
        if (simulationActive) {
            pauseSimulation();
        } else {
            resumeSimulation();
        }
    });

    // Stop Transfer Button
    document.getElementById('stop-transfer').addEventListener('click', () => {
        stopSimulation();
    });

    // Reset All Button
    document.getElementById('reset-all').addEventListener('click', () => {
        resetSimulation();
    });

    // Clear Log Button
    document.getElementById('clear-log').addEventListener('click', () => {
        const logContent = document.getElementById('log-content');
        logContent.innerHTML = '<div class="log-entry info"><span class="log-time">[00:00:00]</span><span class="log-message">Log cleared by user.</span></div>';
        addLogEntry('Log cleared', 'info');
    });

    // Export Log Button
    document.getElementById('export-log').addEventListener('click', () => {
        exportLog();
    });

    // Log Level Filter
    document.getElementById('log-level').addEventListener('change', (e) => {
        filterLogEntries(e.target.value);
    });
}

/**
 * Load System Information
 */
function loadSystemInfo() {
    fetch('/api/system-info')
        .then(response => response.json())
        .then(data => {
            updateSystemInfoUI(data.profile);
            currentOS = data.os;

            // Highlight active OS card
            document.querySelectorAll('.os-card').forEach(card => {
                if (card.dataset.os === currentOS) {
                    card.classList.add('active');
                }
            });
        })
        .catch(error => {
            console.error('Error loading system info:', error);
            addLogEntry('Error loading system information', 'warning');
        });
}

/**
 * Switch Operating System
 */
function switchOS(os) {
    fetch('/api/switch-os', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ os: os })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateSystemInfoUI(data.profile);

                // Update comparison chart with OS-specific efficiency
                updateComparisonChart(os);
            }
        })
        .catch(error => {
            console.error('Error switching OS:', error);
            addLogEntry('Error switching operating system', 'error');
        });
}

/**
 * Update System Information UI
 */
function updateSystemInfoUI(profile) {
    // Update sidebar specs
    document.getElementById('scheduler-type').textContent = profile.scheduler_type;
    document.getElementById('dma-priority').textContent = profile.dma_priority.replace('_', ' ').toUpperCase();
    document.getElementById('context-switch').textContent = `${profile.context_switch_overhead} cycles`;
    document.getElementById('max-bandwidth').textContent = `${profile.max_dma_bandwidth} MB/s`;
    document.getElementById('cpu-cores-spec').textContent = profile.cpu_cores;
    document.getElementById('clock-speed').textContent = `${profile.clock_speed_ghz} GHz`;

    // Update top nav
    document.getElementById('system-name').textContent = profile.name;
    document.getElementById('cpu-info').textContent = `${profile.cpu_cores} Cores`;

    // Store current profile for reference
    if (!systemProfiles[currentOS]) {
        systemProfiles[currentOS] = profile;
    }
}

/**
 * Setup System Profiles
 */
function setupSystemProfiles() {
    fetch('/api/system-comparison')
        .then(response => response.json())
        .then(data => {
            systemProfiles = data;
            console.log('System profiles loaded:', systemProfiles);
        })
        .catch(error => {
            console.error('Error loading system profiles:', error);
        });
}

/**
 * Get Current System Profile
 */
function getCurrentSystemProfile() {
    return systemProfiles[currentOS] || systemProfiles['windows'];
}

// Expose for file_upload.js
window.SystemProfiles = {
    getCurrentProfile: getCurrentSystemProfile
};
/**
 * Start Simulation
 */
function startSimulation() {
    if (!fileUpload.getCurrentFile()) {
        addLogEntry('Please upload a file first!', 'warning');
        return;
    }

    // Reset charts
    resetChartData();

    // Emit start simulation event
    socket.emit('start_simulation', {
        mode: currentMode
    });

    // Update UI
    addLogEntry(``, 'info'); // Spacer
    addLogEntry(`🚀 STARTING SIMULATION - ${currentMode.toUpperCase()} MODE`, 'info');

    const profile = getCurrentSystemProfile();
    addLogEntry(`   OS: ${profile.name}`, 'info');
    addLogEntry(`   Scheduler: ${profile.scheduler_type}`, 'info');
    addLogEntry(`   Bandwidth: ${profile.max_dma_bandwidth} MB/s`, 'info');
    addLogEntry(`   Context Switch: ${profile.context_switch_overhead} cycles`, 'info');

    if (currentFileInfo) {
        addLogEntry(`   File: ${currentFileInfo.name} (${currentFileInfo.size_mb} MB)`, 'info');
        addLogEntry(`   File Type: ${currentFileInfo.type}`, 'info');
        addLogEntry(`   Complexity: ${currentFileInfo.complexity}`, 'info');
    }

    addLogEntry(``, 'info'); // Spacer
}

/**
 * Pause Simulation
 */
function pauseSimulation() {
    window.globalSocket.emit('pause_simulation');
    simulationActive = false;
    document.getElementById('pause-transfer').innerHTML = '<i class="fas fa-play"></i> Resume';
}

/**
 * Resume Simulation
 */
function resumeSimulation() {
    window.globalSocket.emit('resume_simulation');
    simulationActive = true;
    document.getElementById('pause-transfer').innerHTML = '<i class="fas fa-pause"></i> Pause';
}

/**
 * Stop Simulation
 */
function stopSimulation() {
    window.globalSocket.emit('stop_simulation');
    handleSimulationStop();
}

/**
 * Reset Simulation
 */
function resetSimulation() {
    // Reset UI elements
    resetChartData();
    resetMetricsUI();

    // Reset buttons
    document.getElementById('start-transfer').disabled = !fileUpload.getCurrentFile();
    document.getElementById('pause-transfer').disabled = true;
    document.getElementById('stop-transfer').disabled = true;
    document.getElementById('pause-transfer').innerHTML = '<i class="fas fa-pause"></i> Pause';

    // Reset status
    updateStatus('IDLE', 'idle');

    // Clear analytics section
    document.getElementById('analytics-section').style.display = 'none';

    addLogEntry('Simulation reset', 'info');
}

/**
 * Update Real-time Metrics
 */
function updateMetrics(data) {
    // Update chart data
    chartData.cpu.shift();
    chartData.cpu.push(data.cpu_utilization || 0);
    chartData.dma.shift();
    chartData.dma.push(data.dma_utilization || 0);
    chartData.bus.shift();
    chartData.bus.push(data.bus_utilization || 0);
    chartData.throughput.shift();
    chartData.throughput.push(data.throughput_mbps || 0);

    // Update charts
    charts.cpu.data.datasets[0].data = [...chartData.cpu];
    charts.cpu.update('none');
    charts.dma.data.datasets[0].data = [...chartData.dma];
    charts.dma.update('none');
    charts.bus.data.datasets[0].data = [...chartData.bus];
    charts.bus.update('none');
    charts.throughput.data.datasets[0].data = [...chartData.throughput];
    charts.throughput.update('none');

    // Update summary cards
    document.getElementById('cpu-util-value').textContent = `${(data.cpu_utilization || 0).toFixed(1)}%`;
    document.getElementById('dma-util-value').textContent = `${(data.dma_utilization || 0).toFixed(1)}%`;
    document.getElementById('bus-util-value').textContent = `${(data.bus_utilization || 0).toFixed(1)}%`;
    document.getElementById('throughput-value').textContent = `${(data.throughput_mbps || 0).toFixed(2)} MB/s`;

    // Update tooltips
    document.getElementById('cpu-cycles-tooltip').textContent = `${data.total_cycles ? data.total_cycles.toLocaleString() : 0} cycles`;
    document.getElementById('dma-channels-tooltip').textContent = `${Math.round((data.dma_utilization || 0) / 25)}/4 channels`;
    document.getElementById('bus-bandwidth-tooltip').textContent = `${((data.bus_utilization || 0) * 2).toFixed(1)} MB/s`;
    document.getElementById('throughput-speed-tooltip').textContent = `${(data.throughput_mbps || 0).toFixed(2)} MB/s`;

    // Update progress
    document.getElementById('progress-fill').style.width = `${data.progress || 0}%`;
    document.getElementById('progress-text').textContent = `${(data.progress || 0).toFixed(1)}%`;
    document.getElementById('transferred-mb').textContent = `${(data.mb_transferred || 0).toFixed(2)} MB`;
    document.getElementById('elapsed-time').textContent = `${(data.elapsed_time || 0).toFixed(1)}s`;

    // Update transfer details
    document.getElementById('current-speed').textContent = `${(data.throughput_mbps || 0).toFixed(2)} MB/s`;
    document.getElementById('chunks-processed').textContent = `${data.chunk || 0}/${data.total_chunks || 0}`;

    // Update cycles
    document.getElementById('current-cycles').textContent = data.total_cycles ? data.total_cycles.toLocaleString() : '0';
    document.getElementById('total-cycles').textContent = data.total_cycles ? data.total_cycles.toLocaleString() : '0';

    // Calculate estimated time remaining
    if (data.elapsed_time > 0 && data.progress > 0) {
        const estimatedTotalTime = data.elapsed_time / (data.progress / 100);
        const remainingTime = estimatedTotalTime - data.elapsed_time;
        document.getElementById('estimated-time').textContent = `${remainingTime.toFixed(1)}s`;
    }
}

/**
 * Handle Simulation Complete
 */
function handleSimulationComplete(data) {
    simulationActive = false;

    // Update UI
    document.getElementById('start-transfer').disabled = false;
    document.getElementById('pause-transfer').disabled = true;
    document.getElementById('stop-transfer').disabled = true;
    updateStatus('COMPLETE', 'idle');

    // Update final stats
    document.getElementById('total-cycles').textContent = data.total_cycles.toLocaleString();
    document.getElementById('efficiency-value').textContent = `${data.efficiency.toFixed(1)}%`;
    document.getElementById('context-switches').textContent = data.cpu_stats.context_switches;
    document.getElementById('instruction-count').textContent = data.cpu_stats.instruction_count.toLocaleString();
    document.getElementById('cycles-per-instruction').textContent = data.cpu_stats.cycles_per_instruction.toFixed(2);

    // Store results for analytics
    if (!window.simulationResults) {
        window.simulationResults = {};
    }
    window.simulationResults[currentMode] = data;

    // Log completion details
    addLogEntry(``, 'info'); // Spacer
    addLogEntry(`✅ SIMULATION COMPLETE - ${currentMode.toUpperCase()} MODE`, 'success');
    addLogEntry(`   Total Time: ${data.total_time.toFixed(3)}s`, 'success');
    addLogEntry(`   Throughput: ${data.throughput_mbps.toFixed(2)} MB/s`, 'success');
    addLogEntry(`   Total Cycles: ${data.total_cycles.toLocaleString()}`, 'success');
    addLogEntry(`   Efficiency: ${data.efficiency.toFixed(2)}%`, 'success');
    addLogEntry(`   CPU Utilization: ${data.cpu_stats.active_percentage.toFixed(2)}%`, 'success');

    if (currentMode === 'dma') {
        addLogEntry(`   DMA Utilization: ${data.dma_stats.avg_dma_utilization.toFixed(2)}%`, 'success');
        addLogEntry(`   Cycles Saved: ${data.dma_stats.total_cycles_saved.toLocaleString()}`, 'success');
    }

    addLogEntry(``, 'info'); // Spacer

    // Check if we have both CPU and DMA results to show analytics
    if (window.simulationResults.cpu && window.simulationResults.dma) {
        setTimeout(() => {
            generateAnalyticsReport();
        }, 1000);
    }
}

/**
 * Handle Simulation Stop
 */
function handleSimulationStop() {
    simulationActive = false;
    document.getElementById('start-transfer').disabled = !fileUpload.getCurrentFile();
    document.getElementById('pause-transfer').disabled = true;
    document.getElementById('stop-transfer').disabled = true;
    document.getElementById('pause-transfer').innerHTML = '<i class="fas fa-pause"></i> Pause';
    updateStatus('IDLE', 'idle');
}

/**
 * Generate Analytics Report
 */
function generateAnalyticsReport() {
    socket.emit('get_analytics');
    addLogEntry('Generating performance analytics report...', 'info');
}

/**
 * Display Analytics Report
 */
function displayAnalyticsReport(report) {
    // Show analytics section
    document.getElementById('analytics-section').style.display = 'grid';

    // Update efficiency score
    const cpuScore = AnalyticsEngine.calculateEfficiencyScore(report.cpu_mode, 'cpu');
    const dmaScore = AnalyticsEngine.calculateEfficiencyScore(report.dma_mode, 'dma');

    document.getElementById('efficiency-score').textContent = `${dmaScore.toFixed(1)}/100`;

    // Update comparison stats
    document.getElementById('comparison-stats').style.display = 'block';
    document.getElementById('time-saved').textContent = `${report.comparison.time_saved_percent.toFixed(1)}% faster`;
    document.getElementById('cycles-saved').textContent = `${report.comparison.cycles_saved_percent.toFixed(1)}% fewer cycles`;
    document.getElementById('throughput-gain').textContent = `${report.comparison.throughput_improvement_percent.toFixed(1)}% higher`;

    // Update comparison chart
    charts.comparison.data.datasets[0].data = [
        report.cpu_mode.efficiency,
        report.dma_mode.efficiency
    ];
    charts.comparison.update();

    // Update bottleneck analysis
    const bottlenecks = AnalyticsEngine.getBottleneckAnalysis(
        report.cpu_mode,
        report.dma_mode,
        'dma'
    );

    if (bottlenecks.length > 0 && bottlenecks[0].component !== 'None') {
        document.getElementById('bottleneck').textContent = bottlenecks[0].component;
        document.getElementById('bottleneck-desc').textContent = bottlenecks[0].issue;
    } else {
        document.getElementById('bottleneck').textContent = 'None';
        document.getElementById('bottleneck-desc').textContent = 'System performing optimally';
    }

    // Update recommendations
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = '';

    report.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>[${rec.priority}]</strong> ${rec.message}`;
        li.style.borderLeftColor = rec.priority === 'HIGH' ? '#ef4444' :
            rec.priority === 'MEDIUM' ? '#f59e0b' : '#10b981';
        recommendationsList.appendChild(li);
    });

    // Log analytics summary
    addLogEntry(``, 'info'); // Spacer
    addLogEntry(`📊 ANALYTICS REPORT GENERATED`, 'info');
    addLogEntry(`   DMA vs CPU Time Saved: ${report.comparison.time_saved_percent.toFixed(1)}%`, 'info');
    addLogEntry(`   Cycles Saved: ${report.comparison.cycles_saved_percent.toFixed(1)}%`, 'info');
    addLogEntry(`   Throughput Improvement: ${report.comparison.throughput_improvement_percent.toFixed(1)}%`, 'info');
    addLogEntry(`   Efficiency Score (DMA): ${dmaScore.toFixed(1)}/100`, 'info');
    addLogEntry(``, 'info'); // Spacer

    // Show recommendations in log
    report.recommendations.forEach(rec => {
        addLogEntry(`💡 [${rec.priority}] ${rec.message}`, 'info');
    });
}

/**
 * Reset Chart Data
 */
function resetChartData() {
    chartData.cpu = Array(chartDataLength).fill(0);
    chartData.dma = Array(chartDataLength).fill(0);
    chartData.bus = Array(chartDataLength).fill(0);
    chartData.throughput = Array(chartDataLength).fill(0);
}

/**
 * Reset Metrics UI
 */
function resetMetricsUI() {
    // Reset summary cards
    document.getElementById('cpu-util-value').textContent = '0%';
    document.getElementById('dma-util-value').textContent = '0%';
    document.getElementById('bus-util-value').textContent = '0%';
    document.getElementById('throughput-value').textContent = '0 MB/s';

    // Reset progress
    document.getElementById('progress-fill').style.width = '0%';
    document.getElementById('progress-text').textContent = '0%';
    document.getElementById('transferred-mb').textContent = '0 MB';
    document.getElementById('elapsed-time').textContent = '0.0s';
    document.getElementById('current-speed').textContent = '0 MB/s';
    document.getElementById('estimated-time').textContent = '--';
    document.getElementById('chunks-processed').textContent = '0/0';

    // Reset cycles
    document.getElementById('current-cycles').textContent = '0';
    document.getElementById('total-cycles').textContent = '0';
    document.getElementById('efficiency-value').textContent = '0%';
    document.getElementById('context-switches').textContent = '0';
    document.getElementById('instruction-count').textContent = '0';
    document.getElementById('cycles-per-instruction').textContent = '0.00';
}

/**
 * Update System Status
 */
function updateStatus(text, state) {
    document.getElementById('system-status-text').textContent = text;
    const dot = document.querySelector('.status-dot');
    dot.className = 'status-dot';
    dot.classList.add(`status-${state}`);
}

/**
 * Update Comparison Chart
 */
function updateComparisonChart(osType) {
    const cpuEfficiency = {
        'windows': 38,
        'linux': 45,
        'macos': 42,
        'android': 35
    };
    const dmaEfficiency = {
        'windows': 92,
        'linux': 96,
        'macos': 94,
        'android': 88
    };

    charts.comparison.data.datasets[0].data = [
        cpuEfficiency[osType] || 40,
        dmaEfficiency[osType] || 95
    ];
    charts.comparison.update();
}

/**
 * Export Log
 */
function exportLog() {
    const logContent = document.getElementById('log-content');
    const logText = Array.from(logContent.children)
        .map(entry => {
            const time = entry.querySelector('.log-time').textContent;
            const message = entry.querySelector('.log-message').textContent;
            return `${time} ${message}`;
        })
        .join('\n');

    const blob = new Blob([logText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `dma_simulator_log_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    addLogEntry('Log exported successfully', 'success');
}

/**
 * Filter Log Entries
 */
function filterLogEntries(level) {
    const logEntries = document.querySelectorAll('.log-entry');

    logEntries.forEach(entry => {
        if (level === 'all') {
            entry.style.display = 'flex';
        } else if (level === 'info') {
            entry.style.display = entry.classList.contains('info') ? 'flex' : 'none';
        } else {
            entry.style.display = entry.classList.contains(level) ? 'flex' : 'none';
        }
    });
}

/**
 * Analytics Engine (Client-side helpers)
 */
const AnalyticsEngine = {
    calculateEfficiencyScore: function (results, mode) {
        let score = 0;

        // Throughput contribution (max 30 points)
        const throughput = results.throughput || results.throughput_mbps;
        score += Math.min(30, (throughput / 10) * 30);

        // Time efficiency (max 30 points)
        const timeScore = 30 - Math.min(30, (results.total_time / 10) * 30);
        score += Math.max(0, timeScore);

        // Cycle efficiency (max 20 points)
        const cycles = results.total_cycles;
        const cycleScore = 20 - Math.min(20, (cycles / 1000000) * 20);
        score += Math.max(0, cycleScore);

        // Mode bonus (max 20 points)
        if (mode === 'dma') {
            score += 15;
        } else {
            score += 5;
        }

        return Math.min(100, Math.round(score * 100) / 100);
    },

    getBottleneckAnalysis: function (cpuStats, dmaStats, mode) {
        const bottlenecks = [];

        if (mode === 'cpu') {
            if (cpuStats.active_percentage > 90) {
                bottlenecks.push({
                    component: 'CPU',
                    issue: `CPU maxed out at ${cpuStats.active_percentage.toFixed(1)}% utilization`
                });
            }

            if (cpuStats.context_switches > 100) {
                bottlenecks.push({
                    component: 'Context Switching',
                    issue: `${cpuStats.context_switches} context switches causing overhead`
                });
            }
        } else {
            if (dmaStats.avg_dma_utilization > 90) {
                bottlenecks.push({
                    component: 'DMA Controller',
                    issue: `DMA at ${dmaStats.avg_dma_utilization.toFixed(1)}% utilization`
                });
            }

            if (dmaStats.avg_bus_utilization > 85) {
                bottlenecks.push({
                    component: 'Memory Bus',
                    issue: `Bus at ${dmaStats.avg_bus_utilization.toFixed(1)}% utilization`
                });
            }
        }

        if (bottlenecks.length === 0) {
            bottlenecks.push({
                component: 'None',
                issue: 'No significant bottlenecks detected'
            });
        }

        return bottlenecks;
    }
};

// Make AnalyticsEngine available globally
window.AnalyticsEngine = AnalyticsEngine;