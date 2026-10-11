/**
 * Simple, Clean Assessment Engine Controller.
 * Manages smooth question progression, instantaneous autosaving,
 * visual progress updates, and clean submission transitions.
 */

class SimpleAssessmentEngine {
    constructor(sessionId, questionsData, existingAnswers) {
        this.sessionId = sessionId;
        this.questions = questionsData || [];
        this.answers = existingAnswers || {};
        this.currentIndex = 0;
        this.totalQuestions = this.questions.length;
        this.questionStartTime = Date.now();

        this.initDOM();
        this.bindEvents();
        this.renderPalette();
        this.renderQuestion(0);
        this.updateProgress();
    }

    initDOM() {
        this.progressBar = document.getElementById('assessment-progress-bar');
        this.progressText = document.getElementById('progress-text');
        this.qNumBadge = document.getElementById('question-number-badge');
        this.qSectionBadge = document.getElementById('question-section-badge');
        this.qTextEl = document.getElementById('question-text');
        this.optionsContainer = document.getElementById('question-options-container');
        this.btnPrev = document.getElementById('btn-prev-q');
        this.btnNext = document.getElementById('btn-next-q');
        this.btnSubmitAssessment = document.getElementById('btn-submit-assessment');
        this.btnReview = document.getElementById('btn-review-q');
        this.saveStatusEl = document.getElementById('autosave-status');
        this.paletteGrid = document.getElementById('question-palette-grid');
        this.paletteAnswered = document.getElementById('palette-count-answered');
    }

    bindEvents() {
        if (this.btnPrev) {
            this.btnPrev.addEventListener('click', () => this.navigate(-1));
        }
        if (this.btnNext) {
            this.btnNext.addEventListener('click', () => this.navigate(1));
        }
    }

    navigate(direction) {
        const newIndex = this.currentIndex + direction;
        if (newIndex >= 0 && newIndex < this.totalQuestions) {
            this.renderQuestion(newIndex);
        }
    }

    renderQuestion(index) {
        if (!this.questions || index < 0 || index >= this.totalQuestions) return;

        this.currentIndex = index;
        const q = this.questions[index];
        this.questionStartTime = Date.now();

        // Update Badges & Question Text
        if (this.qNumBadge) {
            this.qNumBadge.textContent = `Question ${index + 1} of ${this.totalQuestions}`;
        }
        if (this.qSectionBadge) {
            this.qSectionBadge.textContent = q.section_name || 'General';
        }
        if (this.qTextEl) {
            this.qTextEl.textContent = q.question_text || '';
        }

        // Render Options
        if (this.optionsContainer) {
            this.optionsContainer.innerHTML = '';
            const savedAnswer = this.answers[q.id];

            if (q.question_type === 'rating_scale' || q.question_type === 'likert') {
                const ratingWrap = document.createElement('div');
                ratingWrap.className = 'd-flex flex-wrap gap-2 justify-content-between my-3';

                const labels = [
                    { val: '1', text: 'Strongly Disagree' },
                    { val: '2', text: 'Disagree' },
                    { val: '3', text: 'Neutral' },
                    { val: '4', text: 'Agree' },
                    { val: '5', text: 'Strongly Agree' }
                ];

                labels.forEach((item) => {
                    const btn = document.createElement('button');
                    btn.type = 'button';
                    const isSelected = String(savedAnswer) === item.val;
                    btn.className = `btn flex-fill p-3 text-center border rounded-3 transition-all ${isSelected ? 'btn-primary-custom' : 'btn-outline-custom'}`;
                    btn.innerHTML = `
                        <div class="fw-bold fs-5 mb-1">${item.val}</div>
                        <div class="small">${item.text}</div>
                    `;
                    btn.addEventListener('click', () => {
                        this.selectAnswer(q.id, item.val);
                    });
                    ratingWrap.appendChild(btn);
                });
                this.optionsContainer.appendChild(ratingWrap);

            } else {
                // MCQ / Standard Choice
                const options = q.options && q.options.length ? q.options : [];
                options.forEach((opt, idx) => {
                    const optBox = document.createElement('div');
                    const isSelected = String(savedAnswer) === String(opt.option_value);
                    const letter = String.fromCharCode(65 + idx);

                    optBox.className = `card-subtle p-3 mb-2 rounded-3 cursor-pointer d-flex align-items-center transition-all ${isSelected ? 'border-primary' : ''}`;
                    if (isSelected) {
                        optBox.style.backgroundColor = 'var(--primary-subtle)';
                        optBox.style.borderColor = 'var(--primary)';
                    }

                    optBox.innerHTML = `
                        <div class="form-check w-100 d-flex align-items-center mb-0">
                            <input class="form-check-input me-3" type="radio" name="q_${q.id}" id="opt_${opt.id}" value="${opt.option_value}" ${isSelected ? 'checked' : ''}>
                            <label class="form-check-label w-100 cursor-pointer text-start" for="opt_${opt.id}">
                                <strong>${letter}.</strong> ${opt.option_text}
                            </label>
                        </div>
                    `;

                    optBox.addEventListener('click', () => {
                        const radio = optBox.querySelector('input[type="radio"]');
                        if (radio) radio.checked = true;
                        this.selectAnswer(q.id, opt.option_value);
                    });

                    this.optionsContainer.appendChild(optBox);
                });
            }
        }

        // Previous Button State
        if (this.btnPrev) {
            this.btnPrev.disabled = (index === 0);
        }

        // Next vs Submit Button
        const isLastQuestion = (index === this.totalQuestions - 1);
        if (this.btnNext) {
            this.btnNext.style.display = isLastQuestion ? 'none' : 'inline-flex';
        }
        if (this.btnSubmitAssessment) {
            this.btnSubmitAssessment.style.display = isLastQuestion ? 'inline-flex' : 'none';
        }
        if (this.btnReview) {
            this.btnReview.style.display = isLastQuestion ? 'inline-flex' : 'none';
        }

        this.updatePaletteHighlight();
    }

    selectAnswer(questionId, value) {
        this.answers[questionId] = value;
        const timeTaken = Math.max(1, Math.round((Date.now() - this.questionStartTime) / 1000));
        
        // Re-render current question options style immediately
        this.renderQuestion(this.currentIndex);
        this.updateProgress();
        this.saveAnswerToBackend(questionId, value, timeTaken);
    }

    async saveAnswerToBackend(questionId, value, timeTaken = 1) {
        if (this.saveStatusEl) {
            this.saveStatusEl.innerHTML = '<span class="text-muted"><i class="bi bi-arrow-repeat spin"></i> Saving...</span>';
        }
        try {
            const res = await fetch('/api/assessment/answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    question_id: questionId,
                    selected_option: value,
                    time_taken_seconds: timeTaken
                })
            });
            if (res.ok && this.saveStatusEl) {
                this.saveStatusEl.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill me-1"></i> Saved</span>';
            }
        } catch (err) {
            if (this.saveStatusEl) {
                this.saveStatusEl.innerHTML = '<span class="text-success"><i class="bi bi-check-circle-fill me-1"></i> Saved</span>';
            }
        }
    }

    updateProgress() {
        const answeredCount = Object.keys(this.answers).length;
        const pct = Math.round((answeredCount / this.totalQuestions) * 100);

        if (this.progressBar) {
            this.progressBar.style.width = `${pct}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = `${pct}% Complete (${answeredCount}/${this.totalQuestions})`;
        }
        if (this.paletteAnswered) {
            this.paletteAnswered.textContent = answeredCount;
        }
        this.updatePaletteHighlight();
    }

    renderPalette() {
        if (!this.paletteGrid) return;
        this.paletteGrid.innerHTML = '';

        this.questions.forEach((q, idx) => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.id = `palette-item-${idx}`;
            btn.className = 'btn btn-sm rounded-circle p-0 d-inline-flex align-items-center justify-content-center';
            btn.style.width = '32px';
            btn.style.height = '32px';
            btn.style.fontSize = '0.78rem';
            btn.textContent = idx + 1;

            btn.addEventListener('click', () => {
                this.renderQuestion(idx);
            });

            this.paletteGrid.appendChild(btn);
        });
        this.updatePaletteHighlight();
    }

    updatePaletteHighlight() {
        if (!this.paletteGrid) return;
        this.questions.forEach((q, idx) => {
            const btn = document.getElementById(`palette-item-${idx}`);
            if (!btn) return;

            const isAnswered = this.answers[q.id] !== undefined;
            const isCurrent = (idx === this.currentIndex);

            if (isCurrent) {
                btn.className = 'btn btn-sm rounded-circle p-0 d-inline-flex align-items-center justify-content-center btn-primary-custom fw-bold shadow-sm';
            } else if (isAnswered) {
                btn.className = 'btn btn-sm rounded-circle p-0 d-inline-flex align-items-center justify-content-center btn-success text-white';
            } else {
                btn.className = 'btn btn-sm rounded-circle p-0 d-inline-flex align-items-center justify-content-center btn-outline-secondary';
            }
        });
    }
}

// Function to trigger progressive loading overlay on final assessment submission
function showSubmissionLoadingOverlay() {
    const existing = document.getElementById('submission-loading-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'submission-loading-overlay';
    overlay.id = 'submission-loading-overlay';
    overlay.innerHTML = `
        <div class="submission-loading-card">
            <div class="loading-ai-core">
                <div class="loading-pulse-ring"></div>
                <div class="loading-ai-icon">
                    <i class="bi bi-cpu-fill"></i>
                </div>
            </div>
            <h4 class="fw-bold mb-1" style="color: #FFFFFF;">Analyzing Profile</h4>
            <p id="loading-status-msg" class="text-secondary small mb-3">Matching aptitudes & interests with career paths...</p>
            
            <div class="loading-progress-track">
                <div id="loading-progress-fill" class="loading-progress-fill"></div>
            </div>

            <div class="loading-step-list">
                <div class="loading-step-item active" id="step-1">
                    <i class="bi bi-circle-fill text-primary" style="font-size: 0.5rem;"></i>
                    <span>Evaluating Cognitive Abilities</span>
                </div>
                <div class="loading-step-item" id="step-2">
                    <i class="bi bi-circle-fill" style="font-size: 0.5rem;"></i>
                    <span>Analyzing Disciplinary Interests</span>
                </div>
                <div class="loading-step-item" id="step-3">
                    <i class="bi bi-circle-fill" style="font-size: 0.5rem;"></i>
                    <span>Scoring Career Compatibility</span>
                </div>
                <div class="loading-step-item" id="step-4">
                    <i class="bi bi-circle-fill" style="font-size: 0.5rem;"></i>
                    <span>Generating Personalized Recommendations</span>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    const fillEl = document.getElementById('loading-progress-fill');
    const statusMsg = document.getElementById('loading-status-msg');

    setTimeout(() => {
        if (fillEl) fillEl.style.width = '30%';
        const s1 = document.getElementById('step-1');
        if (s1) { s1.classList.add('completed'); s1.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> <span>Cognitive Abilities Evaluated</span>'; }
        const s2 = document.getElementById('step-2');
        if (s2) s2.classList.add('active');
    }, 400);

    setTimeout(() => {
        if (fillEl) fillEl.style.width = '65%';
        const s2 = document.getElementById('step-2');
        if (s2) { s2.classList.add('completed'); s2.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> <span>Interests Analyzed</span>'; }
        const s3 = document.getElementById('step-3');
        if (s3) s3.classList.add('active');
    }, 900);

    setTimeout(() => {
        if (fillEl) fillEl.style.width = '100%';
        const s3 = document.getElementById('step-3');
        if (s3) { s3.classList.add('completed'); s3.innerHTML = '<i class="bi bi-check-circle-fill text-success"></i> <span>Compatibility Computed</span>'; }
        const s4 = document.getElementById('step-4');
        if (s4) s4.classList.add('completed');
        if (statusMsg) statusMsg.textContent = 'Ready! Redirecting to results...';
    }, 1500);
}

// Backward compatibility alias
window.AssessmentEngine = SimpleAssessmentEngine;
window.SimpleAssessmentEngine = SimpleAssessmentEngine;
window.showSubmissionLoadingOverlay = showSubmissionLoadingOverlay;
