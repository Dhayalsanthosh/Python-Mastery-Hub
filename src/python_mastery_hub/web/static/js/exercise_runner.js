// Location: src/python_mastery_hub/web/static/js/exercise_runner.js

/**
 * Exercise Runner for Python Mastery Hub
 * Handles exercise execution, testing, submission, and progress tracking
 */

class ExerciseRunner {
  constructor(exerciseId, options = {}) {
    this.exerciseId = exerciseId;
    this.options = {
      autoSave: true,
      showHints: true,
      enableTesting: true,
      enableSubmission: true,
      trackProgress: true,
      ...options,
    };

    this.state = {
      status: "not_started", // not_started, in_progress, testing, completed, failed
      attempts: 0,
      hintsUsed: 0,
      startTime: null,
      lastSaveTime: null,
      testResults: [],
      score: 0,
      feedback: null,
    };

    this.codeEditor = null;
    this.testRunner = null;
    this.progressTracker = null;

    this.init();
  }

  /**
   * Initialize the exercise runner
   */
  async init() {
    try {
      await this.loadExerciseData();
      this.setupUI();
      this.setupEventListeners();
      this.loadProgress();

      if (this.options.trackProgress) {
        this.startSession();
      }
    } catch (error) {
      console.error("Failed to initialize exercise runner:", error);
      this.showError("Failed to load exercise. Please refresh the page.");
    }
  }

  /**
   * Load exercise data from the server
   */
  async loadExerciseData() {
    const response = await fetch(`/api/exercises/${this.exerciseId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
    });

    if (!response.ok) {
      throw new Error("Failed to load exercise data");
    }

    this.exerciseData = await response.json();
  }

  /**
   * Setup the user interface
   */
  setupUI() {
    this.setupCodeEditor();
    this.setupTestRunner();
    this.setupProgressTracker();
    this.updateUI();
  }

  /**
   * Setup the code editor
   */
  setupCodeEditor() {
    const editorContainer = document.getElementById("code-editor");
    if (editorContainer && window.CodeEditor) {
      this.codeEditor = new CodeEditor("code-editor", {
        starter: this.exerciseData.starter_code || "",
        autoSave: this.options.autoSave,
        language: "python",
      });

      // Listen for code changes
      editorContainer.addEventListener("codeChanged", (event) => {
        this.onCodeChange(event.detail.code);
      });
    }
  }

  /**
   * Setup the test runner interface
   */
  setupTestRunner() {
    if (!this.options.enableTesting) return;

    this.testRunner = {
      runTests: async (code) => {
        return await this.executeTests(code);
      },
      showResults: (results) => {
        this.displayTestResults(results);
      },
    };
  }

  /**
   * Setup progress tracking
   */
  setupProgressTracker() {
    if (!this.options.trackProgress) return;

    this.progressTracker = {
      updateProgress: (progress) => {
        this.updateProgressDisplay(progress);
      },
      saveState: () => {
        this.saveProgress();
      },
    };
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Run code button
    const runButton = document.getElementById("run-code-btn");
    if (runButton) {
      runButton.addEventListener("click", () => this.runCode());
    }

    // Test code button
    const testButton = document.getElementById("test-code-btn");
    if (testButton) {
      testButton.addEventListener("click", () => this.runTests());
    }

    // Submit solution button
    const submitButton = document.getElementById("submit-solution-btn");
    if (submitButton) {
      submitButton.addEventListener("click", () => this.submitSolution());
    }

    // Hint button
    const hintButton = document.getElementById("get-hint-btn");
    if (hintButton) {
      hintButton.addEventListener("click", () => this.showHint());
    }

    // Reset button
    const resetButton = document.getElementById("reset-code-btn");
    if (resetButton) {
      resetButton.addEventListener("click", () => this.resetCode());
    }

    // Auto-save on visibility change
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.saveProgress();
      }
    });

    // Save on page unload
    window.addEventListener("beforeunload", () => {
      this.saveProgress();
    });
  }

  /**
   * Start a new exercise session
   */
  startSession() {
    this.state.startTime = Date.now();
    this.state.status = "in_progress";
    this.trackEvent("exercise_started", {
      exercise_id: this.exerciseId,
      timestamp: this.state.startTime,
    });
  }

  /**
   * Handle code changes
   */
  onCodeChange(code) {
    if (this.state.status === "not_started") {
      this.startSession();
    }

    // Auto-save
    if (this.options.autoSave) {
      clearTimeout(this.autoSaveTimer);
      this.autoSaveTimer = setTimeout(() => {
        this.saveProgress();
      }, 2000);
    }

    // Clear previous test results if code changed significantly
    this.clearPreviousResults();
  }

  /**
   * Run the current code
   */
  async runCode() {
    const code = this.getCode();
    if (!code.trim()) {
      this.showMessage("Please write some code first.", "warning");
      return;
    }

    this.setLoadingState("run-code-btn", true);
    this.clearOutput();

    try {
      const response = await fetch("/api/code/execute", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          code: code,
          exercise_id: this.exerciseId,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        this.displayOutput(result);
        this.trackEvent("code_executed", {
          exercise_id: this.exerciseId,
          success: true,
          execution_time: result.execution_time,
        });
      } else {
        this.displayError(result.error || "Execution failed");
      }
    } catch (error) {
      this.displayError("Network error: " + error.message);
    } finally {
      this.setLoadingState("run-code-btn", false);
    }
  }

  /**
   * Run tests on the current code
   */
  async runTests() {
    const code = this.getCode();
    if (!code.trim()) {
      this.showMessage("Please write some code first.", "warning");
      return;
    }

    this.state.attempts++;
    this.state.status = "testing";
    this.setLoadingState("test-code-btn", true);
    this.clearTestResults();

    try {
      const results = await this.executeTests(code);
      this.state.testResults = results.tests;
      this.displayTestResults(results);

      if (results.all_passed) {
        this.onAllTestsPassed(results);
      } else {
        this.onTestsFailed(results);
      }
    } catch (error) {
      this.displayError("Test execution failed: " + error.message);
      this.state.status = "failed";
    } finally {
      this.setLoadingState("test-code-btn", false);
    }
  }

  /**
   * Execute tests for the current code
   */
  async executeTests(code) {
    const response = await fetch("/api/exercises/test", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
      body: JSON.stringify({
        exercise_id: this.exerciseId,
        code: code,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || "Test execution failed");
    }

    return await response.json();
  }

  /**
   * Handle when all tests pass
   */
  onAllTestsPassed(results) {
    this.state.status = "completed";
    this.state.score = results.score;

    this.showMessage(
      "🎉 All tests passed! You can now submit your solution.",
      "success"
    );
    this.enableSubmissionButton();

    this.trackEvent("tests_passed", {
      exercise_id: this.exerciseId,
      attempts: this.state.attempts,
      score: this.state.score,
    });
  }

  /**
   * Handle when tests fail
   */
  onTestsFailed(results) {
    this.state.status = "in_progress";
    const failedCount = results.tests.filter((t) => !t.passed).length;

    this.showMessage(
      `${failedCount} test(s) failed. Review the results and try again.`,
      "warning"
    );

    this.trackEvent("tests_failed", {
      exercise_id: this.exerciseId,
      attempts: this.state.attempts,
      failed_count: failedCount,
    });
  }

  /**
   * Submit the solution
   */
  async submitSolution() {
    if (this.state.status !== "completed") {
      this.showMessage("Please pass all tests before submitting.", "warning");
      return;
    }

    const code = this.getCode();
    const confirmation = confirm(
      "Are you sure you want to submit your solution?"
    );

    if (!confirmation) return;

    this.setLoadingState("submit-solution-btn", true);

    try {
      const response = await fetch("/api/exercises/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          exercise_id: this.exerciseId,
          code: code,
          time_taken: this.getTimeSpent(),
          attempts: this.state.attempts,
          hints_used: this.state.hintsUsed,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        this.onSubmissionSuccess(result);
      } else {
        this.showMessage(result.message || "Submission failed", "error");
      }
    } catch (error) {
      this.showMessage("Network error: " + error.message, "error");
    } finally {
      this.setLoadingState("submit-solution-btn", false);
    }
  }

  /**
   * Handle successful submission
   */
  onSubmissionSuccess(result) {
    this.state.feedback = result.feedback;

    // Show success message
    this.showMessage("🎉 Solution submitted successfully!", "success");

    // Show completion modal or redirect
    this.showCompletionModal(result);

    // Track completion
    this.trackEvent("exercise_completed", {
      exercise_id: this.exerciseId,
      score: result.score,
      time_taken: this.getTimeSpent(),
      attempts: this.state.attempts,
      hints_used: this.state.hintsUsed,
    });

    // Clear saved progress
    this.clearSavedProgress();
  }

  /**
   * Show a hint to the user
   */
  showHint() {
    if (!this.exerciseData.hints || this.exerciseData.hints.length === 0) {
      this.showMessage("No hints available for this exercise.", "info");
      return;
    }

    const hintIndex = this.state.hintsUsed;
    if (hintIndex >= this.exerciseData.hints.length) {
      this.showMessage("No more hints available.", "info");
      return;
    }

    const hint = this.exerciseData.hints[hintIndex];
    this.displayHint(hint, hintIndex + 1);

    this.state.hintsUsed++;
    this.trackEvent("hint_used", {
      exercise_id: this.exerciseId,
      hint_index: hintIndex,
    });
  }

  /**
   * Reset the code to starter template
   */
  resetCode() {
    const confirmation = confirm(
      "Are you sure you want to reset your code? This cannot be undone."
    );
    if (!confirmation) return;

    if (this.codeEditor) {
      this.codeEditor.setValue(this.exerciseData.starter_code || "");
    }

    this.clearOutput();
    this.clearTestResults();
    this.state.status = "not_started";

    this.trackEvent("code_reset", {
      exercise_id: this.exerciseId,
    });
  }

  /**
   * Display test results
   */
  displayTestResults(results) {
    const container = document.getElementById("test-results");
    if (!container) return;

    container.innerHTML = "";

    const header = document.createElement("div");
    header.className = "test-results-header";
    header.innerHTML = `
            <h4>Test Results</h4>
            <span class="test-summary ${
              results.all_passed ? "passed" : "failed"
            }">
                ${results.passed}/${results.total} tests passed
            </span>
        `;
    container.appendChild(header);

    results.tests.forEach((test, index) => {
      const testElement = document.createElement("div");
      testElement.className = `test-case ${test.passed ? "passed" : "failed"}`;

      testElement.innerHTML = `
                <div class="test-header">
                    <i class="fas ${test.passed ? "fa-check" : "fa-times"}"></i>
                    <span class="test-name">${test.name}</span>
                </div>
                <div class="test-description">${test.description}</div>
                ${
                  !test.passed
                    ? `
                    <div class="test-failure">
                        <strong>Expected:</strong> ${test.expected}<br>
                        <strong>Got:</strong> ${test.actual}
                        ${
                          test.error
                            ? `<br><strong>Error:</strong> ${test.error}`
                            : ""
                        }
                    </div>
                `
                    : ""
                }
            `;

      container.appendChild(testElement);
    });
  }

  /**
   * Display code output
   */
  displayOutput(result) {
    const container = document.getElementById("code-output");
    if (!container) return;

    container.innerHTML = "";

    if (result.stdout) {
      const output = document.createElement("div");
      output.className = "output-section stdout";
      output.innerHTML = `
                <h5>Output:</h5>
                <pre>${this.escapeHtml(result.stdout)}</pre>
            `;
      container.appendChild(output);
    }

    if (result.stderr) {
      const error = document.createElement("div");
      error.className = "output-section stderr";
      error.innerHTML = `
                <h5>Errors:</h5>
                <pre>${this.escapeHtml(result.stderr)}</pre>
            `;
      container.appendChild(error);
    }

    if (result.execution_time) {
      const timing = document.createElement("div");
      timing.className = "execution-time";
      timing.textContent = `Executed in ${result.execution_time}ms`;
      container.appendChild(timing);
    }
  }

  /**
   * Display error message
   */
  displayError(error) {
    const container = document.getElementById("code-output");
    if (!container) return;

    container.innerHTML = `
            <div class="output-section error">
                <h5>Error:</h5>
                <pre>${this.escapeHtml(error)}</pre>
            </div>
        `;
  }

  /**
   * Display hint
   */
  displayHint(hint, hintNumber) {
    const modal = document.createElement("div");
    modal.className = "hint-modal";
    modal.innerHTML = `
            <div class="hint-content">
                <div class="hint-header">
                    <h4>Hint ${hintNumber}</h4>
                    <button class="close-hint" onclick="this.closest('.hint-modal').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="hint-body">
                    ${hint}
                </div>
            </div>
        `;

    document.body.appendChild(modal);

    // Auto-remove after 10 seconds
    setTimeout(() => {
      if (modal.parentNode) {
        modal.remove();
      }
    }, 10000);
  }

  /**
   * Show completion modal
   */
  showCompletionModal(result) {
    const modal = document.createElement("div");
    modal.className = "completion-modal";
    modal.innerHTML = `
            <div class="completion-content">
                <div class="completion-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <h3>Congratulations!</h3>
                <p>You've successfully completed this exercise!</p>
                
                <div class="completion-stats">
                    <div class="stat">
                        <span class="stat-value">${result.score}%</span>
                        <span class="stat-label">Score</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${this.formatTime(
                          this.getTimeSpent()
                        )}</span>
                        <span class="stat-label">Time</span>
                    </div>
                    <div class="stat">
                        <span class="stat-value">${this.state.attempts}</span>
                        <span class="stat-label">Attempts</span>
                    </div>
                </div>
                
                <div class="completion-actions">
                    <a href="/exercises/${
                      result.next_exercise_id
                    }" class="btn btn-primary">
                        Next Exercise
                    </a>
                    <a href="/exercises" class="btn btn-outline">
                        More Exercises
                    </a>
                    <button onclick="this.closest('.completion-modal').remove()" class="btn btn-secondary">
                        Close
                    </button>
                </div>
            </div>
        `;

    document.body.appendChild(modal);
  }

  /**
   * Save exercise progress
   */
  saveProgress() {
    if (!this.options.autoSave) return;

    const progress = {
      exercise_id: this.exerciseId,
      code: this.getCode(),
      state: this.state,
      timestamp: Date.now(),
    };

    localStorage.setItem(
      `exercise_progress_${this.exerciseId}`,
      JSON.stringify(progress)
    );
    this.state.lastSaveTime = Date.now();
  }

  /**
   * Load saved progress
   */
  loadProgress() {
    const saved = localStorage.getItem(`exercise_progress_${this.exerciseId}`);
    if (!saved) return;

    try {
      const progress = JSON.parse(saved);

      // Restore state
      this.state = { ...this.state, ...progress.state };

      // Restore code if available and not starter code
      if (progress.code && progress.code !== this.exerciseData.starter_code) {
        if (this.codeEditor) {
          this.codeEditor.setValue(progress.code);
        }
      }

      this.updateUI();
    } catch (error) {
      console.error("Failed to load progress:", error);
    }
  }

  /**
   * Clear saved progress
   */
  clearSavedProgress() {
    localStorage.removeItem(`exercise_progress_${this.exerciseId}`);
  }

  /**
   * Update UI based on current state
   */
  updateUI() {
    // Update status indicator
    const statusElement = document.querySelector(".exercise-status");
    if (statusElement) {
      statusElement.textContent = this.state.status
        .replace("_", " ")
        .toUpperCase();
      statusElement.className = `exercise-status ${this.state.status}`;
    }

    // Update progress
    if (this.progressTracker) {
      this.progressTracker.updateProgress(this.calculateProgress());
    }

    // Enable/disable buttons based on state
    this.updateButtonStates();
  }

  /**
   * Update button states
   */
  updateButtonStates() {
    const submitButton = document.getElementById("submit-solution-btn");
    if (submitButton) {
      submitButton.disabled = this.state.status !== "completed";
    }
  }

  /**
   * Enable submission button
   */
  enableSubmissionButton() {
    const submitButton = document.getElementById("submit-solution-btn");
    if (submitButton) {
      submitButton.disabled = false;
      submitButton.classList.add("enabled");
    }
  }

  /**
   * Calculate exercise progress percentage
   */
  calculateProgress() {
    let progress = 0;

    if (this.state.status === "in_progress") progress = 25;
    else if (this.state.status === "testing") progress = 50;
    else if (this.state.status === "completed") progress = 100;

    return progress;
  }

  /**
   * Update progress display
   */
  updateProgressDisplay(progress) {
    const progressBar = document.querySelector(".exercise-progress-bar");
    if (progressBar) {
      progressBar.style.width = `${progress}%`;
    }

    const progressText = document.querySelector(".exercise-progress-text");
    if (progressText) {
      progressText.textContent = `${progress}% Complete`;
    }
  }

  /**
   * Get current code from editor
   */
  getCode() {
    return this.codeEditor ? this.codeEditor.getValue() : "";
  }

  /**
   * Get time spent on exercise
   */
  getTimeSpent() {
    return this.state.startTime ? Date.now() - this.state.startTime : 0;
  }

  /**
   * Format time in readable format
   */
  formatTime(milliseconds) {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
      return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }

  /**
   * Set loading state for button
   */
  setLoadingState(buttonId, loading) {
    const button = document.getElementById(buttonId);
    if (!button) return;

    if (loading) {
      button.disabled = true;
      button.classList.add("loading");
      const icon = button.querySelector("i");
      if (icon) {
        icon.className = "fas fa-spinner fa-spin";
      }
    } else {
      button.disabled = false;
      button.classList.remove("loading");
      const icon = button.querySelector("i");
      if (icon) {
        // Restore original icon
        const originalIcon = button.getAttribute("data-icon") || "fas fa-play";
        icon.className = originalIcon;
      }
    }
  }

  /**
   * Clear output display
   */
  clearOutput() {
    const container = document.getElementById("code-output");
    if (container) {
      container.innerHTML = "";
    }
  }

  /**
   * Clear test results display
   */
  clearTestResults() {
    const container = document.getElementById("test-results");
    if (container) {
      container.innerHTML = "";
    }
  }

  /**
   * Clear previous results
   */
  clearPreviousResults() {
    this.clearOutput();
    this.clearTestResults();
  }

  /**
   * Show message to user
   */
  showMessage(message, type = "info") {
    const messageContainer =
      document.getElementById("messages") || this.createMessageContainer();

    const messageElement = document.createElement("div");
    messageElement.className = `message message-${type}`;
    messageElement.innerHTML = `
            <i class="fas ${this.getMessageIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentNode.remove()" class="message-close">
                <i class="fas fa-times"></i>
            </button>
        `;

    messageContainer.appendChild(messageElement);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (messageElement.parentNode) {
        messageElement.remove();
      }
    }, 5000);
  }

  /**
   * Create message container
   */
  createMessageContainer() {
    const container = document.createElement("div");
    container.id = "messages";
    container.className = "messages-container";
    document.body.appendChild(container);
    return container;
  }

  /**
   * Get icon for message type
   */
  getMessageIcon(type) {
    const icons = {
      success: "fa-check-circle",
      error: "fa-exclamation-circle",
      warning: "fa-exclamation-triangle",
      info: "fa-info-circle",
    };
    return icons[type] || icons.info;
  }

  /**
   * Show error message
   */
  showError(message) {
    this.showMessage(message, "error");
  }

  /**
   * Escape HTML to prevent XSS
   */
  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Track analytics event
   */
  trackEvent(eventName, data) {
    fetch("/api/analytics/track", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("authToken")}`,
      },
      body: JSON.stringify({
        event: eventName,
        data: data,
        timestamp: Date.now(),
      }),
    }).catch((error) => {
      console.error("Failed to track event:", error);
    });
  }

  /**
   * Dispose of the exercise runner
   */
  dispose() {
    if (this.autoSaveTimer) {
      clearTimeout(this.autoSaveTimer);
    }

    if (this.codeEditor && this.codeEditor.dispose) {
      this.codeEditor.dispose();
    }

    this.saveProgress();
  }
}

// Export for global use
window.ExerciseRunner = ExerciseRunner;

// Auto-initialize on exercise pages
document.addEventListener("DOMContentLoaded", () => {
  const exerciseContainer = document.querySelector("[data-exercise-id]");
  if (exerciseContainer) {
    const exerciseId = exerciseContainer.dataset.exerciseId;
    const options = JSON.parse(exerciseContainer.dataset.options || "{}");
    window.currentExerciseRunner = new ExerciseRunner(exerciseId, options);
  }
});
