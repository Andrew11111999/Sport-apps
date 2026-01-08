class WorkoutTimer {
    constructor(sessionId, exercises) {
        this.sessionId = sessionId;
        this.exercises = exercises;
        this.currentExerciseIndex = -1;
        this.currentSet = 0;
        this.isRunning = false;
        this.timeLeft = 0;
        this.totalTime = 0;
        this.timerInterval = null;
        this.currentState = 'idle'; // idle, preparation, work, rest, completed

        this.initializeTimer();
        this.setupEventListeners();
    }

    initializeTimer() {
        this.timerDisplay = document.getElementById('timer');
        this.exerciseDisplay = document.getElementById('current-exercise');
        this.stateDisplay = document.getElementById('timer-state');
        this.progressBar = document.getElementById('workout-progress');
        this.startBtn = document.getElementById('start-btn');
        this.pauseBtn = document.getElementById('pause-btn');
        this.nextBtn = document.getElementById('next-btn');
        this.completeBtn = document.getElementById('complete-btn');

        this.updateDisplay();
    }

    setupEventListeners() {
        this.startBtn.addEventListener('click', () => this.startWorkout());
        this.pauseBtn.addEventListener('click', () => this.togglePause());
        this.nextBtn.addEventListener('click', () => this.nextStep());
        this.completeBtn.addEventListener('click', () => this.completeWorkout());

        // Обработка видимости страницы для паузы
        document.addEventListener('visibilitychange', () => {
            if (document.hidden && this.isRunning) {
                this.togglePause();
            }
        });
    }

    startWorkout() {
        this.startBtn.classList.add('d-none');
        this.pauseBtn.classList.remove('d-none');
        this.nextBtn.classList.remove('d-none');
        this.isRunning = true;
        this.startPreparation();
    }

    startPreparation() {
        this.currentState = 'preparation';
        this.timeLeft = 10; // 10 секунд на подготовку
        this.exerciseDisplay.textContent = 'Приготовьтесь';
        this.stateDisplay.textContent = 'Подготовка к тренировке';
        this.stateDisplay.className = 'text-warning';
        this.startTimer();
    }

    startExercise() {
        if (this.currentExerciseIndex >= this.exercises.length) {
            this.completeWorkout();
            return;
        }

        const exercise = this.exercises[this.currentExerciseIndex];
        this.currentState = 'work';
        this.currentSet = 1;
        this.timeLeft = 30; // 30 секунд на выполнение

        this.exerciseDisplay.textContent = exercise.name;
        this.stateDisplay.textContent = Подход ${this.currentSet}/${exercise.sets}: ${exercise.reps};
        this.stateDisplay.className = 'text-success';

        this.highlightCurrentExercise();
        this.updateProgress();
        this.startTimer();

        // Сохраняем начало упражнения
        this.saveExerciseProgress(exercise.id, this.currentSet);
    }

    startRest() {
        const exercise = this.exercises[this.currentExerciseIndex];
        this.currentState = 'rest';
        this.timeLeft = exercise.rest_time;

        this.exerciseDisplay.textContent = 'Отдых';
        this.stateDisplay.textContent = Отдыхайте перед ${this.currentSet === exercise.sets ? 'следующим упражнением' : 'следующим подходом'};
        this.stateDisplay.className = 'text-info';

        this.startTimer();
    }

    startTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        this.updateTimerDisplay();
        this.timerInterval = setInterval(() => {
            this.timeLeft--;

Andrei, [08.01.2026 19:22]
this.totalTime++;
            this.updateTimerDisplay();

            if (this.timeLeft <= 0) {
                clearInterval(this.timerInterval);
                this.handleTimerComplete();
            }
        }, 1000);
    }

    handleTimerComplete() {
        switch (this.currentState) {
            case 'preparation':
                this.currentExerciseIndex = 0;
                this.startExercise();
                break;

            case 'work':
                const exercise = this.exercises[this.currentExerciseIndex];
                this.currentSet++;

                if (this.currentSet > exercise.sets) {
                    // Все подходы выполнены
                    if (this.currentExerciseIndex < this.exercises.length - 1) {
                        this.startRest();
                    } else {
                        this.completeWorkout();
                    }
                } else {
                    // Следующий подход
                    this.startRest();
                }
                break;

            case 'rest':
                this.startExercise();
                break;
        }
    }

    nextStep() {
        clearInterval(this.timerInterval);

        switch (this.currentState) {
            case 'preparation':
                this.currentExerciseIndex = 0;
                this.startExercise();
                break;
            case 'work':
            case 'rest':
                this.handleTimerComplete();
                break;
        }
    }

    updateTimerDisplay() {
        const minutes = Math.floor(this.timeLeft / 60);
        const seconds = this.timeLeft % 60;
        this.timerDisplay.textContent =
            ${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')};

        // Изменение цвета при малом времени
        if (this.timeLeft <= 5 && this.currentState !== 'preparation') {
            this.timerDisplay.className = 'display-4 fw-bold text-danger';
        } else {
            this.timerDisplay.className = 'display-4 fw-bold text-primary';
        }
    }

    updateProgress() {
        const totalExercises = this.exercises.length;
        const progress = ((this.currentExerciseIndex + 1) / totalExercises) * 100;
        this.progressBar.style.width = ${progress}%;
        this.progressBar.setAttribute('aria-valuenow', progress);
    }

    highlightCurrentExercise() {
        document.querySelectorAll('.exercise-item').forEach((item, index) => {
            item.classList.remove('active', 'bg-primary', 'text-white', 'bg-success');

            if (index === this.currentExerciseIndex) {
                item.classList.add('active', 'bg-primary', 'text-white');
            } else if (index < this.currentExerciseIndex) {
                item.classList.add('bg-success', 'text-white');
            }
        });
    }

    togglePause() {
        this.isRunning = !this.isRunning;

        if (this.isRunning) {
            this.startTimer();
            this.pauseBtn.innerHTML = '<i class="fas fa-pause me-2"></i>Пауза';
            this.pauseBtn.classList.remove('btn-warning');
            this.pauseBtn.classList.add('btn-secondary');
        } else {
            clearInterval(this.timerInterval);
            this.pauseBtn.innerHTML = '<i class="fas fa-play me-2"></i>Продолжить';
            this.pauseBtn.classList.remove('btn-secondary');
            this.pauseBtn.classList.add('btn-warning');
        }
    }

    async saveExerciseProgress(exerciseId, currentSet) {
        try {
            const response = await fetch('/api/save-exercise/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',

Andrei, [08.01.2026 19:22]
'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    exercise_id: exerciseId,
                    completed_sets: currentSet,
                })
            });

            const data = await response.json();
            if (data.status !== 'success') {
                console.error('Ошибка сохранения:', data.message);
            }
        } catch (error) {
            console.error('Ошибка сети:', error);
        }
    }

    async completeWorkout() {
        clearInterval(this.timerInterval);
        this.currentState = 'completed';
        this.isRunning = false;

        this.exerciseDisplay.textContent = 'Тренировка завершена!';
        this.stateDisplay.textContent = 'Отличная работа! 🎉';
        this.stateDisplay.className = 'text-success';
        this.timerDisplay.textContent = '🎊';

        this.pauseBtn.classList.add('d-none');
        this.nextBtn.classList.add('d-none');
        this.completeBtn.classList.remove('d-none');

        // Сохраняем завершение тренировки
        await this.saveWorkoutCompletion();

        this.showCompletionStats();
    }

    async saveWorkoutCompletion() {
        try {
            const response = await fetch(/workout/session/${this.sessionId}/complete/, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
            });

            const data = await response.json();
            if (data.status === 'success') {
                this.showNotification('Тренировка сохранена!', 'success');
            }
        } catch (error) {
            console.error('Ошибка сохранения:', error);
            this.showNotification('Ошибка сохранения', 'error');
        }
    }

    showCompletionStats() {
        const totalMinutes = Math.floor(this.totalTime / 60);
        const statsHtml =
            <div class="alert alert-success mt-3">
                <h5 class="alert-heading">Отличная работа! 🎉</h5>
                <hr>
                <div class="row text-center">
                    <div class="col-4">
                        <div class="h4 text-primary">${this.exercises.length}</div>
                        <small>Упражнений</small>
                    </div>
                    <div class="col-4">
                        <div class="h4 text-success">${totalMinutes}</div>
                        <small>Минут</small>
                    </div>
                    <div class="col-4">
                        <div class="h4 text-info">100%</div>
                        <small>Выполнено</small>
                    </div>
                </div>
            </div>
        ;

        document.querySelector('.card-body').insertAdjacentHTML('beforeend', statsHtml);
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = alert alert-${type} alert-dismissible fade show;
        notification.innerHTML =
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        ;

        document.getElementById('notifications').appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
}

// Инициализация таймера
document.addEventListener('DOMContentLoaded', function() {
    const sessionId = {{ session.id }};
    const exercises = JSON.parse('{{ exercises_json|escapejs }}');

    if (sessionId && exercises) {
        window.workoutTimer = new WorkoutTimer(sessionId, exercises);
    }
});