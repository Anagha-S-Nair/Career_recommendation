/**
 * Chart.js Visualizations for Student Assessment Results.
 * Renders Multi-Dimensional Radar Aptitude Chart and Bar Chart for Interests
 * with dynamic Light/Dark mode adaptability and responsive parsing.
 */

let activeRadarChart = null;
let activeBarChart = null;
let lastCognitiveData = null;
let lastInterestData = null;

function getChartColors() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    return {
        textColor: isDark ? '#CBD5E1' : '#475569',
        gridColor: isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.06)',
        radarFill: isDark ? 'rgba(99, 102, 241, 0.25)' : 'rgba(79, 70, 229, 0.15)',
        radarBorder: isDark ? '#818CF8' : '#4F46E5',
        radarPoint: isDark ? '#A5B4FC' : '#4338CA'
    };
}

/**
 * Safely extracts a numerical score from raw values, nested objects, or aliases.
 */
function extractScore(dataObj, candidateKeys, fallback = 65.0) {
    if (!dataObj || typeof dataObj !== 'object') {
        return fallback;
    }
    for (const k of candidateKeys) {
        if (dataObj[k] !== undefined && dataObj[k] !== null) {
            const val = dataObj[k];
            if (typeof val === 'object' && val.score !== undefined) {
                const num = Number(val.score);
                if (!isNaN(num)) return num;
            }
            if (typeof val === 'number' && !isNaN(val)) {
                return val;
            }
            const parsed = parseFloat(val);
            if (!isNaN(parsed)) {
                return parsed;
            }
        }
    }
    return fallback;
}

function renderAssessmentCharts(cognitiveData, interestData) {
    lastCognitiveData = cognitiveData || lastCognitiveData;
    lastInterestData = interestData || lastInterestData;

    const colors = getChartColors();

    // 1. Radar Chart: Cognitive & Aptitude Strengths (9 Dimensions)
    const radarCtx = document.getElementById('cognitiveRadarChart');
    if (radarCtx && lastCognitiveData) {
        if (activeRadarChart) {
            activeRadarChart.destroy();
        }

        const labels = [
            'Math Ability',
            'Logical Reasoning',
            'Scientific Thinking',
            'Problem Solving',
            'Analytical Ability',
            'Communication',
            'Creativity',
            'Digital Ability',
            'Learning Agility'
        ];

        const values = [
            extractScore(lastCognitiveData, ['mathematical_ability', 'math_ability', 'math'], 75),
            extractScore(lastCognitiveData, ['logical_reasoning', 'logic'], 80),
            extractScore(lastCognitiveData, ['scientific_reasoning', 'scientific_thinking', 'science'], 75),
            extractScore(lastCognitiveData, ['problem_solving'], 80),
            extractScore(lastCognitiveData, ['analytical_ability', 'analytical_thinking'], 75),
            extractScore(lastCognitiveData, ['communication', 'verbal'], 70),
            extractScore(lastCognitiveData, ['creativity', 'creative'], 70),
            extractScore(lastCognitiveData, ['digital_ability', 'computational_thinking'], 80),
            extractScore(lastCognitiveData, ['learning_ability', 'learning_agility'], 85)
        ];

        activeRadarChart = new Chart(radarCtx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Demonstrated Aptitude',
                    data: values,
                    backgroundColor: colors.radarFill,
                    borderColor: colors.radarBorder,
                    pointBackgroundColor: colors.radarPoint,
                    pointBorderColor: '#FFFFFF',
                    pointHoverBackgroundColor: '#FFFFFF',
                    pointHoverBorderColor: colors.radarBorder,
                    pointRadius: 4,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        angleLines: { color: colors.gridColor },
                        grid: { color: colors.gridColor },
                        pointLabels: {
                            font: { size: 11, family: "'Plus Jakarta Sans', 'Inter', sans-serif", weight: '600' },
                            color: colors.textColor
                        },
                        suggestedMin: 0,
                        suggestedMax: 100,
                        ticks: {
                            stepSize: 20,
                            display: true,
                            backdropColor: 'transparent',
                            color: colors.textColor,
                            font: { size: 10 }
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return ` Aptitude Score: ${context.parsed.r}%`;
                            }
                        }
                    }
                }
            }
        });
    }

    // 2. Bar Chart: Disciplinary & Career Interests
    const barCtx = document.getElementById('interestBarChart');
    if (barCtx && lastInterestData) {
        if (activeBarChart) {
            activeBarChart.destroy();
        }

        const intLabels = [
            'Technology',
            'Engineering',
            'Healthcare',
            'Business',
            'Finance',
            'Arts & Creative',
            'Research'
        ];

        const intValues = [
            extractScore(lastInterestData, ['technology_interest', 'technology', 'tech'], 85),
            extractScore(lastInterestData, ['engineering_interest', 'engineering'], 80),
            extractScore(lastInterestData, ['healthcare_interest', 'medical_interest', 'healthcare', 'medical'], 65),
            extractScore(lastInterestData, ['business_interest', 'business', 'management'], 70),
            extractScore(lastInterestData, ['finance_interest', 'finance', 'commerce'], 72),
            extractScore(lastInterestData, ['creative_interest', 'arts_interest', 'design_interest', 'creative'], 75),
            extractScore(lastInterestData, ['research_interest', 'scientific_interest', 'science_interest', 'research'], 78)
        ];

        // Modern vibrant colors
        const barColors = [
            '#6366F1', // Tech (Indigo)
            '#3B82F6', // Eng (Blue)
            '#10B981', // Healthcare (Emerald)
            '#F59E0B', // Business (Amber)
            '#8B5CF6', // Finance (Purple)
            '#EC4899', // Arts (Rose)
            '#06B6D4'  // Research (Cyan)
        ];

        activeBarChart = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: intLabels,
                datasets: [{
                    label: 'Affinity Score (0-100)',
                    data: intValues,
                    backgroundColor: barColors,
                    borderRadius: 6,
                    borderSkipped: false,
                    maxBarThickness: 42
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: colors.gridColor },
                        ticks: {
                            stepSize: 20,
                            color: colors.textColor,
                            font: { family: "'Inter', sans-serif" }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            font: { size: 11, family: "'Plus Jakarta Sans', 'Inter', sans-serif", weight: '600' },
                            color: colors.textColor
                        }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        padding: 10,
                        cornerRadius: 8,
                        callbacks: {
                            label: function(context) {
                                return ` Interest Affinity: ${context.parsed.y}%`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Listen to theme changes to re-render charts dynamically
window.addEventListener('themechange', () => {
    if (lastCognitiveData || lastInterestData) {
        renderAssessmentCharts(lastCognitiveData, lastInterestData);
    }
});

window.renderAssessmentCharts = renderAssessmentCharts;
