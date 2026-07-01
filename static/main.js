// Tab Navigation
function switchTab(buttons, panels, clickedBtn) {
    if (clickedBtn.classList.contains('active')) return;

    let currentPanel = null;
    panels.forEach(p => {
        if (p.classList.contains('active')) {
            currentPanel = p;
        }
    });

    const targetPanel = document.getElementById(clickedBtn.dataset.target);

    buttons.forEach(b => b.classList.remove('active'));
    clickedBtn.classList.add('active');

    if (currentPanel) {
        currentPanel.style.opacity = '0';
        setTimeout(() => {
            currentPanel.classList.remove('active');
            currentPanel.style.opacity = '';

            targetPanel.classList.add('active');
            void targetPanel.offsetWidth;
            targetPanel.style.opacity = '1';
        }, 250);
    } else {
        targetPanel.classList.add('active');
        targetPanel.style.opacity = '1';
    }
}

const primaryBtns = document.querySelectorAll('.primary-tab');
const primaryPanels = document.querySelectorAll('.tab-panel');
primaryBtns.forEach(btn => {
    btn.addEventListener('click', () => switchTab(primaryBtns, primaryPanels, btn));
});

const subBtns = document.querySelectorAll('.sub-tab');
const subPanels = document.querySelectorAll('.sub-panel');
subBtns.forEach(btn => {
    btn.addEventListener('click', () => switchTab(subBtns, subPanels, btn));
});

// Chart Configuration
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyle = 'circle';
Chart.defaults.plugins.legend.labels.padding = 16;

const COLORS = {
    success: '#86e8a3',
    danger: '#ffb3b0',
    warning: '#ffd98a',
    info: '#b3b0ff',
    accent: '#99caff'
};

const tooltipStyle = {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    titleColor: '#1a202c',
    bodyColor: '#4a5568',
    borderColor: '#e2e8f0',
    borderWidth: 1,
    padding: 12,
    boxPadding: 6,
    usePointStyle: true,
    titleFont: { size: 13, weight: '600' },
    bodyFont: { size: 12 }
};

// Chart Initializations
try {
    new Chart(document.getElementById('chartSourceComparable'), {
        type: 'doughnut',
        data: {
            labels: ['Comparable', 'Non Comparable'],
            datasets: [{
                data: [reportData.totalIntersection, reportData.srcOnlyCount],
                backgroundColor: [COLORS.accent, COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} rows` } }
            }
        }
    });

    new Chart(document.getElementById('chartSourceComparableCols'), {
        type: 'doughnut',
        data: {
            labels: ['Comparable', 'Non Comparable'],
            datasets: [{
                data: [reportData.dataColumns.length, reportData.srcOnlyColumns.length],
                backgroundColor: [COLORS.accent, COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} cols` } }
            }
        }
    });

    new Chart(document.getElementById('chartDestComparable'), {
        type: 'doughnut',
        data: {
            labels: ['Comparable', 'Non Comparable'],
            datasets: [{
                data: [reportData.totalIntersection, reportData.dstnOnlyCount],
                backgroundColor: [COLORS.accent, COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} rows` } }
            }
        }
    });

    new Chart(document.getElementById('chartDestComparableCols'), {
        type: 'doughnut',
        data: {
            labels: ['Comparable', 'Non Comparable'],
            datasets: [{
                data: [reportData.dataColumns.length, reportData.dstnOnlyColumns.length],
                backgroundColor: [COLORS.accent, COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} cols` } }
            }
        }
    });

    new Chart(document.getElementById('chartMatchMismatch'), {
        type: 'doughnut',
        data: {
            labels: ['Fully Matched', 'Mismatched'],
            datasets: [{
                data: [reportData.totalMatched, reportData.totalMismatched],
                backgroundColor: [COLORS.success, COLORS.danger],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} rows` } }
            }
        }
    });

    new Chart(document.getElementById('chartDataQuality'), {
        type: 'doughnut',
        data: {
            labels: ['Clean Rows', 'Rows with Missing Values'],
            datasets: [{
                data: [reportData.totalCleanRows, reportData.totalMissingRows],
                backgroundColor: [COLORS.accent, COLORS.warning],
                borderWidth: 0,
                hoverOffset: 6
            }]
        },
        options: {
            cutout: '60%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed} rows` } }
            }
        }
    });

    new Chart(document.getElementById('chartColumnMismatch'), {
        type: 'bar',
        data: {
            labels: reportData.columnMismatchLabels,
            datasets: [{
                label: 'Mismatches',
                data: reportData.columnMismatchValues,
                backgroundColor: COLORS.danger,
                borderRadius: 4,
                maxBarThickness: 48
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.parsed.y} mismatches` } }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0, color: '#8c95a4' }, grid: { color: '#f0f2f5' } },
                x: { ticks: { color: '#5f6b7a' }, grid: { display: false } }
            }
        }
    });

    new Chart(document.getElementById('chartCompleteness'), {
        type: 'bar',
        data: {
            labels: reportData.completenessLabels,
            datasets: [{
                label: 'Missing Values',
                data: reportData.completenessCombined,
                backgroundColor: COLORS.warning,
                borderRadius: 4,
                maxBarThickness: 48
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { ...tooltipStyle, callbacks: { label: ctx => ` ${ctx.parsed.y} missing values` } }
            },
            scales: {
                y: { beginAtZero: true, ticks: { precision: 0, color: '#8c95a4' }, grid: { color: '#f0f2f5' } },
                x: { ticks: { color: '#5f6b7a' }, grid: { display: false } }
            }
        }
    });
} catch (e) {
    console.warn("Charts could not be initialized. Chart.js may have failed to load.", e);
}


// Zoom Controls
let currentZoom = 1;
const ZOOM_STEP = 0.1;
const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.0;

document.getElementById('zoom-in').addEventListener('click', () => {
    if (currentZoom < MAX_ZOOM) {
        currentZoom = parseFloat((currentZoom + ZOOM_STEP).toFixed(1));
        document.querySelectorAll('.table-wrap').forEach(wrap => {
            wrap.style.setProperty('--table-zoom', currentZoom);
        });
    }
});

document.getElementById('zoom-out').addEventListener('click', () => {
    if (currentZoom > MIN_ZOOM) {
        currentZoom = parseFloat((currentZoom - ZOOM_STEP).toFixed(1));
        document.querySelectorAll('.table-wrap').forEach(wrap => {
            wrap.style.setProperty('--table-zoom', currentZoom);
        });
    }
});

// Pagination & Rendering Logic
let ROWS_PER_PAGE = 50;
const pageState = {
    'sub-all': 1,
    'sub-all-comparable': 1,
    'sub-matched': 1,
    'sub-mismatched': 1,
    'sub-missing': 1,
    'sub-non-comparable-src': 1,
    'sub-non-comparable-dstn': 1,
    'sub-non-comparable-columns': 1
};

// Resolves which data slice each tab should render.
function getDataForTab(tabId) {
    if (tabId === 'sub-all-comparable') {
        return reportData.tableData['sub-comparable'] || [];
    }
    if (tabId === 'sub-non-comparable-src') {
        return (reportData.tableData['sub-non-comparable-records'] || []).filter(r => r.is_src_only);
    }
    if (tabId === 'sub-non-comparable-dstn') {
        return (reportData.tableData['sub-non-comparable-records'] || []).filter(r => r.is_dstn_only);
    }
    return reportData.tableData[tabId] || [];
}

// Used for nulls inside comparable data columns (where the value is genuinely missing within an existing column).
const NULL_SPAN = '<span style="color: #8c95a4; font-style: italic;">null</span>';

function renderTablePage(tabId) {
    const tbody = document.getElementById('tbody-' + tabId.replace('sub-', ''));
    if (!tbody) return;

    const data = getDataForTab(tabId);
    const columns = reportData.dataColumns || [];
    const srcOnlyColumns = reportData.srcOnlyColumns || [];
    const dstnOnlyColumns = reportData.dstnOnlyColumns || [];
    const currentPage = pageState[tabId];

    const totalPages = Math.ceil(data.length / ROWS_PER_PAGE) || 1;
    const startIndex = (currentPage - 1) * ROWS_PER_PAGE;
    const endIndex = Math.min(startIndex + ROWS_PER_PAGE, data.length);
    const pageData = data.slice(startIndex, endIndex);

    const infoSpan = document.getElementById('page-info-' + tabId.replace('sub-', ''));
    if (infoSpan) {
        infoSpan.textContent = `Page ${currentPage} of ${totalPages} (${data.length} total rows)`;
    }

    const prevBtn = document.querySelector(`.page-prev[data-target="${tabId}"]`);
    const nextBtn = document.querySelector(`.page-next[data-target="${tabId}"]`);
    if (prevBtn) prevBtn.disabled = (currentPage === 1);
    if (nextBtn) nextBtn.disabled = (currentPage === totalPages);

    let html = '';

    if (data.length === 0) {
        let msg = "No records found.";
        let colspan = columns.length + 2;

        if (tabId === 'sub-mismatched') {
            msg = "All records match perfectly.";
        } else if (tabId === 'sub-missing') {
            msg = "No records contain missing values.";
        } else if (tabId === 'sub-non-comparable-src') {
            msg = "No non-comparable records in source file.";
            colspan = columns.length + srcOnlyColumns.length + 2;
        } else if (tabId === 'sub-non-comparable-dstn') {
            msg = "No non-comparable records in destination file.";
            colspan = columns.length + dstnOnlyColumns.length + 2;
        } else if (tabId === 'sub-non-comparable-columns') {
            msg = "All columns are comparable.";
            colspan = srcOnlyColumns.length + dstnOnlyColumns.length + 3;
        } else if (tabId === 'sub-all-comparable') {
            msg = "No comparable records found.";
        } else if (tabId === 'sub-all') {
            msg = "No records found.";
            colspan = columns.length + srcOnlyColumns.length + dstnOnlyColumns.length + 2;
        }

        html = `<tr>
            <td colspan="${colspan}" class="empty-state" style="text-align: center; color: #6b7280; padding: 24px;">
                ${msg}
            </td>
        </tr>`;
    } else if (tabId === 'sub-non-comparable-columns') {
        // Side-by-side rendering: file1 ID + src cols | divider | file2 ID + dstn cols
        pageData.forEach(row => {
            html += `<tr>`;

            html += `<td class="col-group-file1 col-id">${row.id_display}</td>`;
            srcOnlyColumns.forEach(col => {
                const val = row[`${col}_src_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file1"><span class="cell-match">${text}</span></td>`;
            });

            html += `<td class="table-divider-cell"></td>`;

            html += `<td class="col-group-file2 col-id">${row.id_display}</td>`;
            dstnOnlyColumns.forEach(col => {
                const val = row[`${col}_dstn_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file2"><span class="cell-match">${text}</span></td>`;
            });

            html += `</tr>`;
        });
    } else if (tabId === 'sub-non-comparable-src') {
        pageData.forEach(row => {
            const rowStatusClass = 'row-status--src';
            const rowClass = 'row-src-only';

            html += `<tr class="${rowClass}">
                <td class="row-status ${rowStatusClass}"></td>
                <td class="col-id">${row.id_display}</td>`;

            columns.forEach(col => {
                const display1 = row[`${col}_1`];
                const text = (display1 === '' || display1 === undefined || display1 === null) ? NULL_SPAN : display1;
                html += `<td><span class="cell-match">${text}</span></td>`;
            });

            srcOnlyColumns.forEach(col => {
                const val = row[`${col}_src_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file1"><span class="cell-match">${text}</span></td>`;
            });

            html += `</tr>`;
        });
    } else if (tabId === 'sub-non-comparable-dstn') {
        pageData.forEach(row => {
            const rowStatusClass = 'row-status--dstn';
            const rowClass = 'row-dstn-only';

            html += `<tr class="${rowClass}">
                <td class="row-status ${rowStatusClass}"></td>
                <td class="col-id">${row.id_display}</td>`;

            columns.forEach(col => {
                const display2 = row[`${col}_2`];
                const text = (display2 === '' || display2 === undefined || display2 === null) ? NULL_SPAN : display2;
                html += `<td><span class="cell-match">${text}</span></td>`;
            });

            dstnOnlyColumns.forEach(col => {
                const val = row[`${col}_dstn_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file2"><span class="cell-match">${text}</span></td>`;
            });

            html += `</tr>`;
        });
    } else if (tabId === 'sub-all') {
        // Unified view: comparable + non-comparable rows mixed
        pageData.forEach(row => {
            let rowStatusClass = 'row-status--match';
            let rowClass = '';

            if (row.is_src_only) {
                rowStatusClass = 'row-status--src';
                rowClass = 'row-src-only';
            } else if (row.is_dstn_only) {
                rowStatusClass = 'row-status--dstn';
                rowClass = 'row-dstn-only';
            } else if (row.has_nan) {
                rowStatusClass = 'row-status--warning';
            } else if (row.has_mismatch) {
                rowStatusClass = 'row-status--mismatch';
            }

            html += `<tr class="${rowClass}">
                <td class="row-status ${rowStatusClass}"></td>
                <td class="col-id">${row.id_display}</td>`;

            // Data columns
            columns.forEach(col => {
                const is_mismatch = row[`${col}_mismatch`];
                const is_nan = row[`${col}_nan`];
                const display1 = row[`${col}_1`];
                const display2 = row[`${col}_2`];

                html += `<td>`;

                if (row.is_src_only) {
                    const text = (display1 === '' || display1 === undefined || display1 === null) ? NULL_SPAN : display1;
                    html += `<span class="cell-match">${text}</span>`;
                } else if (row.is_dstn_only) {
                    const text = (display2 === '' || display2 === undefined || display2 === null) ? NULL_SPAN : display2;
                    html += `<span class="cell-match">${text}</span>`;
                } else if (is_mismatch || is_nan) {
                    html += `
                        <div class="diff-cell">
                            <div class="diff-line diff-line--file1">${display1 || '&nbsp;'}</div>
                            <div class="diff-line diff-line--file2">${display2 || '&nbsp;'}</div>
                        </div>`;
                } else {
                    const text = (display1 === '' || display1 === undefined || display1 === null) ? NULL_SPAN : display1;
                    html += `<span class="cell-match">${text}</span>`;
                }

                html += `</td>`;
            });

            // Src-only columns (blank when not applicable to this row)
            srcOnlyColumns.forEach(col => {
                const val = row[`${col}_src_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file1"><span class="cell-match">${text}</span></td>`;
            });

            // Dstn-only columns (blank when not applicable to this row)
            dstnOnlyColumns.forEach(col => {
                const val = row[`${col}_dstn_only`];
                const text = (val === '' || val === undefined || val === null) ? '' : val;
                html += `<td class="col-group-file2"><span class="cell-match">${text}</span></td>`;
            });

            html += `</tr>`;
        });
    } else {
        // sub-all-comparable, sub-matched, sub-mismatched, sub-missing
        pageData.forEach(row => {
            let rowStatusClass = 'row-status--match';

            if (tabId === 'sub-missing' || row.has_nan) {
                rowStatusClass = 'row-status--warning';
            } else if (tabId === 'sub-mismatched' || row.has_mismatch) {
                rowStatusClass = 'row-status--mismatch';
            }

            html += `<tr>
                <td class="row-status ${rowStatusClass}"></td>
                <td class="col-id">${row.id_display}</td>`;

            columns.forEach(col => {
                const is_mismatch = row[`${col}_mismatch`];
                const is_nan = row[`${col}_nan`];
                const display1 = row[`${col}_1`];
                const display2 = row[`${col}_2`];

                html += `<td>`;

                if (is_mismatch || is_nan) {
                    html += `
                        <div class="diff-cell">
                            <div class="diff-line diff-line--file1">${display1 || '&nbsp;'}</div>
                            <div class="diff-line diff-line--file2">${display2 || '&nbsp;'}</div>
                        </div>`;
                } else {
                    const text = (display1 === '' || display1 === undefined || display1 === null) ? NULL_SPAN : display1;
                    html += `<span class="cell-match">${text}</span>`;
                }

                html += `</td>`;
            });

            html += `</tr>`;
        });
    }

    tbody.innerHTML = html;
}

// Initial render for all tables
document.addEventListener('DOMContentLoaded', () => {
    Object.keys(pageState).forEach(tabId => renderTablePage(tabId));

    document.querySelectorAll('.page-prev').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabId = e.target.getAttribute('data-target');
            if (pageState[tabId] > 1) {
                pageState[tabId]--;
                renderTablePage(tabId);
            }
        });
    });

    document.querySelectorAll('.page-next').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const tabId = e.target.getAttribute('data-target');
            const data = getDataForTab(tabId);
            const totalPages = Math.ceil(data.length / ROWS_PER_PAGE) || 1;
            if (pageState[tabId] < totalPages) {
                pageState[tabId]++;
                renderTablePage(tabId);
            }
        });
    });
});

// Export Dropdown Toggle
const exportToggle = document.getElementById('export-toggle');
const exportMenu = document.getElementById('export-menu');
if (exportToggle && exportMenu) {
    exportToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isVisible = exportMenu.style.display !== 'none';
        exportMenu.style.display = isVisible ? 'none' : 'block';
    });

    document.addEventListener('click', (e) => {
        if (!exportMenu.contains(e.target) && e.target !== exportToggle) {
            exportMenu.style.display = 'none';
        }
    });
}

// Export to Excel Logic
function getActiveTabId() {
    const activeSubTab = document.querySelector('.sub-tab.active');
    return activeSubTab ? activeSubTab.dataset.target : 'sub-all';
}

// Export logic mapped to Python backend
async function downloadExcelFromBackend(payload, filename) {
    try {
        const response = await fetch('/export_excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.statusText}`);
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (err) {
        alert("Failed to export Excel: " + err.message);
    }
}

const exportCurrentBtn = document.getElementById('export-current');
if (exportCurrentBtn) {
    exportCurrentBtn.addEventListener('click', () => {
        const tabId = getActiveTabId();
        const activeSubTab = document.querySelector('.sub-tab.active');
        const tabName = activeSubTab ? activeSubTab.textContent.trim().split(/\s+/)[0] : 'Current Tab';

        const payload = {
            id_col_name: reportData.id_col_name || 'Event Id',
            columns: reportData.dataColumns || [],
            src_only_columns: reportData.srcOnlyColumns || [],
            dstn_only_columns: reportData.dstnOnlyColumns || [],
            tabs: [
                {
                    tab_id: tabId,
                    name: tabName,
                    rows: getDataForTab(tabId)
                }
            ]
        };

        downloadExcelFromBackend(payload, `Comparison_${tabId}.xlsx`);
    });
}

const exportAllBtn = document.getElementById('export-all');
if (exportAllBtn) {
    exportAllBtn.addEventListener('click', () => {
        const tabsInfo = [
            { id: 'sub-all', name: 'All' },
            { id: 'sub-all-comparable', name: 'Comparable' },
            { id: 'sub-matched', name: 'Matched' },
            { id: 'sub-mismatched', name: 'Mismatched' },
            { id: 'sub-missing', name: 'Missing' },
            { id: 'sub-non-comparable-src', name: 'Source Only' },
            { id: 'sub-non-comparable-dstn', name: 'Target Only' },
            { id: 'sub-non-comparable-columns', name: 'Unique Columns' }
        ];

        const payload = {
            id_col_name: reportData.id_col_name || 'Event Id',
            columns: reportData.dataColumns || [],
            src_only_columns: reportData.srcOnlyColumns || [],
            dstn_only_columns: reportData.dstnOnlyColumns || [],
            tabs: tabsInfo.map(t => ({
                tab_id: t.id,
                name: t.name,
                rows: getDataForTab(t.id)
            }))
        };

        downloadExcelFromBackend(payload, `Comparison_Full_Report.xlsx`);
    });
}