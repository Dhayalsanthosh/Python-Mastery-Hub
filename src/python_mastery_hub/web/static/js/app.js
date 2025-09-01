/**
 * Python Mastery Hub - Interactive JavaScript Application
 * Provides dynamic functionality for the learning platform
 */

class PythonMasteryHub {
  constructor() {
    this.apiBase = "/api/v1";
    this.currentModule = null;
    this.userProgress = {};
    this.darkMode = this.getDarkModePreference();

    this.init();
  }

  /**
   * Initialize the application
   */
  init() {
    this.setupEventListeners();
    this.setupDarkMode();
    this.loadUserProgress();
    this.initializeCodeEditors();
    this.setupWebSocket();
    this.setupProgressTracking();

    console.log("Python Mastery Hub initialized successfully! 🐍");
  }

  /**
   * Setup event listeners for interactive elements
   */
  setupEventListeners() {
    // Navigation
    document.addEventListener("DOMContentLoaded", () => {
      this.setupMobileNavigation();
      this.setupModuleNavigation();
      this.setupSearchFunctionality();
      this.setupFormSubmissions();
    });

    // Module cards
    document.querySelectorAll(".module-card").forEach((card) => {
      card.addEventListener("click", (e) => {
        const moduleId = card.dataset.moduleId;
        if (moduleId) {
          this.loadModule(moduleId);
        }
      });
    });

    // Code copy buttons
    document.querySelectorAll(".copy-button").forEach((button) => {
      button.addEventListener("click", (e) => {
        this.copyCodeToClipboard(e.target);
      });
    });

    // Exercise submission
    document.querySelectorAll(".exercise-form").forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.submitExercise(form);
      });
    });

    // Progress tracking
    document.querySelectorAll(".topic-link").forEach((link) => {
      link.addEventListener("click", (e) => {
        const topicId = link.dataset.topicId;
        const moduleId = link.dataset.moduleId;
        if (topicId && moduleId) {
          this.trackProgress(moduleId, topicId, "viewed");
        }
      });
    });
  }

  /**
   * Setup mobile navigation toggle
   */
  setupMobileNavigation() {
    const navToggle = document.querySelector(".navbar-toggle");
    const navMenu = document.querySelector(".navbar-nav");

    if (navToggle && navMenu) {
      navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("active");
        navToggle.setAttribute(
          "aria-expanded",
          navToggle.getAttribute("aria-expanded") === "true" ? "false" : "true"
        );
      });

      // Close menu when clicking outside
      document.addEventListener("click", (e) => {
        if (!navToggle.contains(e.target) && !navMenu.contains(e.target)) {
          navMenu.classList.remove("active");
          navToggle.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  /**
   * Setup module navigation and filtering
   */
  setupModuleNavigation() {
    const difficultyFilter = document.querySelector("#difficulty-filter");
    const searchInput = document.querySelector("#module-search");

    if (difficultyFilter) {
      difficultyFilter.addEventListener("change", () => {
        this.filterModules();
      });
    }

    if (searchInput) {
      searchInput.addEventListener(
        "input",
        this.debounce(() => {
          this.filterModules();
        }, 300)
      );
    }
  }

  /**
   * Setup search functionality
   */
  setupSearchFunctionality() {
    const searchForm = document.querySelector("#search-form");
    const searchInput = document.querySelector("#search-input");

    if (searchForm && searchInput) {
      searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.performSearch(searchInput.value);
      });

      // Auto-suggest as user types
      searchInput.addEventListener(
        "input",
        this.debounce(() => {
          this.showSearchSuggestions(searchInput.value);
        }, 300)
      );
    }
  }

  /**
   * Setup form submissions with validation
   */
  setupFormSubmissions() {
    document.querySelectorAll("form[data-api]").forEach((form) => {
      form.addEventListener("submit", (e) => {
        e.preventDefault();
        this.handleFormSubmission(form);
      });
    });
  }

  /**
   * Setup dark mode toggle
   */
  setupDarkMode() {
    const darkModeToggle = document.querySelector(".dark-mode-toggle");

    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => {
        this.toggleDarkMode();
      });
    }

    // Apply saved dark mode preference
    this.applyDarkMode(this.darkMode);
  }

  /**
   * Initialize code editors with syntax highlighting and features
   */
  initializeCodeEditors() {
    document.querySelectorAll(".code-editor").forEach((editor) => {
      this.enhanceCodeEditor(editor);
    });

    // Setup code execution for interactive examples
    document.querySelectorAll(".run-code-btn").forEach((button) => {
      button.addEventListener("click", (e) => {
        const codeBlock = e.target
          .closest(".code-example")
          .querySelector("code");
        if (codeBlock) {
          this.executeCode(codeBlock.textContent);
        }
      });
    });
  }

  /**
   * Setup WebSocket connection for real-time features
   */
  setupWebSocket() {
    if ("WebSocket" in window) {
      try {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        this.websocket = new WebSocket(wsUrl);

        this.websocket.onopen = () => {
          console.log("WebSocket connected");
          this.sendWebSocketMessage({
            type: "join",
            user: this.getCurrentUser(),
          });
        };

        this.websocket.onmessage = (event) => {
          this.handleWebSocketMessage(JSON.parse(event.data));
        };

        this.websocket.onclose = () => {
          console.log("WebSocket disconnected");
          // Attempt to reconnect after 5 seconds
          setTimeout(() => this.setupWebSocket(), 5000);
        };

        this.websocket.onerror = (error) => {
          console.error("WebSocket error:", error);
        };
      } catch (error) {
        console.warn("WebSocket not available:", error);
      }
    }
  }

  /**
   * Setup progress tracking functionality
   */
  setupProgressTracking() {
    // Track page views
    this.trackPageView();

    // Track time spent on page
    this.startTimeTracking();

    // Setup intersection observer for content engagement
    this.setupContentObserver();
  }

  /**
   * Load a specific learning module
   */
  async loadModule(moduleId) {
    try {
      this.showLoading(`Loading ${moduleId} module...`);

      const response = await fetch(`${this.apiBase}/modules/${moduleId}`);
      if (!response.ok) {
        throw new Error(`Failed to load module: ${response.statusText}`);
      }

      const moduleData = await response.json();
      this.currentModule = moduleData;

      this.displayModule(moduleData);
      this.trackProgress(moduleId, null, "module_opened");

      this.hideLoading();
    } catch (error) {
      console.error("Error loading module:", error);
      this.showError("Failed to load module. Please try again.");
      this.hideLoading();
    }
  }

  /**
   * Display module content
   */
  displayModule(moduleData) {
    const moduleContainer = document.querySelector("#module-content");
    if (!moduleContainer) return;

    moduleContainer.innerHTML = `
            <div class="module-header">
                <h1>${moduleData.name}</h1>
                <span class="module-difficulty difficulty-${
                  moduleData.difficulty
                }">
                    ${moduleData.difficulty}
                </span>
                <p class="module-description">${moduleData.description}</p>
            </div>
            
            <div class="module-topics">
                ${this.renderTopics(moduleData.topics)}
            </div>
            
            <div class="module-examples">
                ${this.renderExamples(moduleData.examples)}
            </div>
            
            <div class="module-exercises">
                ${this.renderExercises(moduleData.exercises)}
            </div>
        `;

    // Re-initialize interactive elements for new content
    this.initializeCodeEditors();
    this.setupEventListeners();
  }

  /**
   * Render module topics
   */
  renderTopics(topics) {
    if (!topics || topics.length === 0) return "";

    return `
            <div class="topics-section">
                <h2>Topics</h2>
                <div class="topics-grid">
                    ${topics
                      .map(
                        (topic) => `
                        <div class="topic-card card" data-topic-id="${
                          topic.id
                        }">
                            <h3>${topic.title}</h3>
                            <p>${topic.description}</p>
                            <div class="topic-progress">
                                <div class="progress">
                                    <div class="progress-bar" style="width: ${this.getTopicProgress(
                                      topic.id
                                    )}%"></div>
                                </div>
                            </div>
                        </div>
                    `
                      )
                      .join("")}
                </div>
            </div>
        `;
  }

  /**
   * Render code examples
   */
  renderExamples(examples) {
    if (!examples) return "";

    return `
            <div class="examples-section">
                <h2>Code Examples</h2>
                ${Object.entries(examples)
                  .map(
                    ([key, example]) => `
                    <div class="code-example">
                        <div class="code-example-header">
                            <span>${key.replace(/_/g, " ").toUpperCase()}</span>
                            <button class="copy-button" title="Copy to clipboard">
                                📋 Copy
                            </button>
                        </div>
                        <pre><code class="language-python">${this.escapeHtml(
                          example
                        )}</code></pre>
                        <button class="btn btn-primary run-code-btn">
                            ▶️ Run Code
                        </button>
                    </div>
                `
                  )
                  .join("")}
            </div>
        `;
  }

  /**
   * Render exercises
   */
  renderExercises(exercises) {
    if (!exercises || exercises.length === 0) return "";

    return `
            <div class="exercises-section">
                <h2>Practice Exercises</h2>
                ${exercises
                  .map(
                    (exercise) => `
                    <div class="exercise-card card" data-exercise-id="${exercise.id}">
                        <div class="card-header">
                            <h3>${exercise.title}</h3>
                            <span class="exercise-difficulty difficulty-${exercise.difficulty}">
                                ${exercise.difficulty}
                            </span>
                        </div>
                        <div class="card-body">
                            <p>${exercise.description}</p>
                            <form class="exercise-form" data-exercise-id="${exercise.id}">
                                <div class="form-group">
                                    <label class="form-label">Your Solution:</label>
                                    <textarea 
                                        class="form-control code-input" 
                                        name="solution" 
                                        rows="10" 
                                        placeholder="Write your Python code here..."
                                        required
                                    ></textarea>
                                </div>
                                <button type="submit" class="btn btn-primary">
                                    Submit Solution
                                </button>
                            </form>
                        </div>
                    </div>
                `
                  )
                  .join("")}
            </div>
        `;
  }

  /**
   * Submit exercise solution
   */
  async submitExercise(form) {
    const exerciseId = form.dataset.exerciseId;
    const solution = form.querySelector('[name="solution"]').value;

    if (!solution.trim()) {
      this.showError("Please enter your solution");
      return;
    }

    try {
      this.showLoading("Evaluating your solution...");

      const response = await fetch(`${this.apiBase}/exercises/submit`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          exercise_id: exerciseId,
          code: solution,
        }),
      });

      const result = await response.json();

      if (response.ok) {
        this.showSuccess("Solution submitted successfully!");
        this.displayExerciseResult(result);
        this.trackProgress(
          this.currentModule.id,
          exerciseId,
          "exercise_completed"
        );
      } else {
        this.showError(result.message || "Failed to submit solution");
      }

      this.hideLoading();
    } catch (error) {
      console.error("Error submitting exercise:", error);
      this.showError("Failed to submit solution. Please try again.");
      this.hideLoading();
    }
  }

  /**
   * Execute code in a safe environment
   */
  async executeCode(code) {
    try {
      this.showLoading("Running code...");

      const response = await fetch(`${this.apiBase}/code/execute`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code }),
      });

      const result = await response.json();
      this.displayCodeResult(result);
      this.hideLoading();
    } catch (error) {
      console.error("Error executing code:", error);
      this.showError("Failed to execute code");
      this.hideLoading();
    }
  }

  /**
   * Copy code to clipboard
   */
  async copyCodeToClipboard(button) {
    const codeBlock = button.closest(".code-example").querySelector("code");
    const code = codeBlock.textContent;

    try {
      await navigator.clipboard.writeText(code);

      const originalText = button.textContent;
      button.textContent = "✅ Copied!";
      button.classList.add("copied");

      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove("copied");
      }, 2000);
    } catch (error) {
      console.error("Failed to copy code:", error);
      this.showError("Failed to copy code to clipboard");
    }
  }

  /**
   * Filter modules based on difficulty and search
   */
  filterModules() {
    const difficultyFilter = document.querySelector("#difficulty-filter");
    const searchInput = document.querySelector("#module-search");
    const moduleCards = document.querySelectorAll(".module-card");

    const selectedDifficulty = difficultyFilter ? difficultyFilter.value : "";
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : "";

    moduleCards.forEach((card) => {
      const difficulty = card.dataset.difficulty || "";
      const title = card.querySelector(".card-title").textContent.toLowerCase();
      const description = card.querySelector("p").textContent.toLowerCase();

      const matchesDifficulty =
        !selectedDifficulty || difficulty === selectedDifficulty;
      const matchesSearch =
        !searchTerm ||
        title.includes(searchTerm) ||
        description.includes(searchTerm);

      card.style.display =
        matchesDifficulty && matchesSearch ? "block" : "none";
    });
  }

  /**
   * Perform search across all content
   */
  async performSearch(query) {
    if (!query.trim()) return;

    try {
      this.showLoading("Searching...");

      const response = await fetch(
        `${this.apiBase}/search?q=${encodeURIComponent(query)}`
      );
      const results = await response.json();

      this.displaySearchResults(results);
      this.hideLoading();
    } catch (error) {
      console.error("Search error:", error);
      this.showError("Search failed. Please try again.");
      this.hideLoading();
    }
  }

  /**
   * Track user progress
   */
  async trackProgress(moduleId, topicId, action) {
    const progressData = {
      module_id: moduleId,
      topic_id: topicId,
      action: action,
      timestamp: new Date().toISOString(),
    };

    try {
      await fetch(`${this.apiBase}/progress`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(progressData),
      });

      // Update local progress
      this.updateLocalProgress(moduleId, topicId, action);
    } catch (error) {
      console.error("Failed to track progress:", error);
    }
  }

  /**
   * Load user progress from API
   */
  async loadUserProgress() {
    try {
      const response = await fetch(`${this.apiBase}/progress`);
      if (response.ok) {
        this.userProgress = await response.json();
        this.updateProgressUI();
      }
    } catch (error) {
      console.error("Failed to load progress:", error);
    }
  }

  /**
   * Update progress UI elements
   */
  updateProgressUI() {
    document.querySelectorAll(".progress-bar").forEach((bar) => {
      const moduleId = bar.dataset.moduleId;
      const topicId = bar.dataset.topicId;

      if (moduleId) {
        const progress = this.getModuleProgress(moduleId);
        bar.style.width = `${progress}%`;
      } else if (topicId) {
        const progress = this.getTopicProgress(topicId);
        bar.style.width = `${progress}%`;
      }
    });
  }

  /**
   * Handle WebSocket messages
   */
  handleWebSocketMessage(message) {
    switch (message.type) {
      case "notification":
        this.showNotification(message.content);
        break;
      case "progress_update":
        this.updateProgressFromWebSocket(message.data);
        break;
      case "new_exercise":
        this.handleNewExercise(message.data);
        break;
      default:
        console.log("Unknown WebSocket message:", message);
    }
  }

  /**
   * Send WebSocket message
   */
  sendWebSocketMessage(message) {
    if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(message));
    }
  }

  /**
   * Setup content observation for engagement tracking
   */
  setupContentObserver() {
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              const elementId = entry.target.id;
              const moduleId = entry.target.dataset.moduleId;
              const topicId = entry.target.dataset.topicId;

              if (moduleId && topicId) {
                this.trackProgress(moduleId, topicId, "content_viewed");
              }
            }
          });
        },
        {
          threshold: 0.5,
          rootMargin: "0px 0px -50px 0px",
        }
      );

      document.querySelectorAll("[data-track-view]").forEach((element) => {
        observer.observe(element);
      });
    }
  }

  /**
   * Enhance code editor with features
   */
  enhanceCodeEditor(editor) {
    // Add line numbers
    const code = editor.querySelector("code");
    if (code) {
      const lines = code.textContent.split("\n");
      const lineNumbers = lines.map((_, i) => i + 1).join("\n");

      if (!editor.querySelector(".line-numbers")) {
        const lineNumbersEl = document.createElement("div");
        lineNumbersEl.className = "line-numbers";
        lineNumbersEl.textContent = lineNumbers;
        editor.insertBefore(lineNumbersEl, code.parentElement);
      }
    }

    // Add syntax highlighting if Prism.js is available
    if (typeof Prism !== "undefined") {
      Prism.highlightAllUnder(editor);
    }
  }

  /**
   * Dark mode functionality
   */
  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    this.applyDarkMode(this.darkMode);
    this.saveDarkModePreference(this.darkMode);
  }

  applyDarkMode(isDark) {
    document.body.classList.toggle("dark-mode", isDark);

    const toggleButton = document.querySelector(".dark-mode-toggle");
    if (toggleButton) {
      toggleButton.textContent = isDark ? "☀️" : "🌙";
      toggleButton.title = isDark
        ? "Switch to light mode"
        : "Switch to dark mode";
    }
  }

  getDarkModePreference() {
    const saved = localStorage.getItem("darkMode");
    if (saved !== null) {
      return JSON.parse(saved);
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  saveDarkModePreference(isDark) {
    localStorage.setItem("darkMode", JSON.stringify(isDark));
  }

  /**
   * Utility functions
   */
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  getCurrentUser() {
    // This would typically get user info from authentication
    return "anonymous_user";
  }

  getModuleProgress(moduleId) {
    return this.userProgress[moduleId]?.overall || 0;
  }

  getTopicProgress(topicId) {
    return this.userProgress.topics?.[topicId] || 0;
  }

  updateLocalProgress(moduleId, topicId, action) {
    if (!this.userProgress[moduleId]) {
      this.userProgress[moduleId] = { topics: {}, overall: 0 };
    }

    if (topicId) {
      this.userProgress[moduleId].topics[topicId] =
        (this.userProgress[moduleId].topics[topicId] || 0) + 10;
    }
  }

  trackPageView() {
    const page = window.location.pathname;
    this.sendAnalytics("page_view", { page });
  }

  startTimeTracking() {
    this.startTime = Date.now();

    window.addEventListener("beforeunload", () => {
      const timeSpent = Date.now() - this.startTime;
      this.sendAnalytics("time_spent", {
        page: window.location.pathname,
        duration: timeSpent,
      });
    });
  }

  sendAnalytics(event, data) {
    // Send analytics data to backend
    fetch(`${this.apiBase}/analytics`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ event, data, timestamp: Date.now() }),
    }).catch((err) => console.warn("Analytics failed:", err));
  }

  /**
   * UI feedback methods
   */
  showLoading(message = "Loading...") {
    const loader =
      document.querySelector("#loading-overlay") || this.createLoader();
    loader.querySelector(".loading-message").textContent = message;
    loader.style.display = "flex";
  }

  hideLoading() {
    const loader = document.querySelector("#loading-overlay");
    if (loader) {
      loader.style.display = "none";
    }
  }

  createLoader() {
    const loader = document.createElement("div");
    loader.id = "loading-overlay";
    loader.innerHTML = `
            <div class="loading-content">
                <div class="spinner"></div>
                <div class="loading-message">Loading...</div>
            </div>
        `;
    loader.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        `;
    document.body.appendChild(loader);
    return loader;
  }

  showError(message) {
    this.showAlert(message, "danger");
  }

  showSuccess(message) {
    this.showAlert(message, "success");
  }

  showNotification(message) {
    this.showAlert(message, "info");
  }

  showAlert(message, type = "info") {
    const alertsContainer =
      document.querySelector("#alerts-container") ||
      this.createAlertsContainer();

    const alert = document.createElement("div");
    alert.className = `alert alert-${type} fade-in`;
    alert.innerHTML = `
            <span>${message}</span>
            <button class="alert-close" onclick="this.parentElement.remove()">×</button>
        `;

    alertsContainer.appendChild(alert);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (alert.parentElement) {
        alert.remove();
      }
    }, 5000);
  }

  createAlertsContainer() {
    const container = document.createElement("div");
    container.id = "alerts-container";
    container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            max-width: 400px;
        `;
    document.body.appendChild(container);
    return container;
  }

  displayCodeResult(result) {
    const resultContainer =
      document.querySelector("#code-result") ||
      this.createCodeResultContainer();

    resultContainer.innerHTML = `
            <div class="code-result-header">
                <h4>Execution Result</h4>
                <button onclick="this.closest('.code-result').style.display='none'">×</button>
            </div>
            <div class="code-result-content">
                ${
                  result.success
                    ? `<div class="result-output"><pre>${result.output}</pre></div>`
                    : `<div class="result-error"><pre>${result.error}</pre></div>`
                }
            </div>
        `;

    resultContainer.style.display = "block";
  }

  createCodeResultContainer() {
    const container = document.createElement("div");
    container.id = "code-result";
    container.className = "code-result card";
    container.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 400px;
            max-height: 300px;
            overflow-y: auto;
            z-index: 1000;
            display: none;
        `;
    document.body.appendChild(container);
    return container;
  }

  displayExerciseResult(result) {
    // Implementation for displaying exercise evaluation results
    console.log("Exercise result:", result);
  }

  displaySearchResults(results) {
    // Implementation for displaying search results
    console.log("Search results:", results);
  }
}

/**
 * Initialize the application when DOM is ready
 */
document.addEventListener("DOMContentLoaded", () => {
  window.pythonMasteryHub = new PythonMasteryHub();
});

/**
 * Service Worker registration for offline support
 */
if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/sw.js")
      .then((registration) => {
        console.log("SW registered: ", registration);
      })
      .catch((registrationError) => {
        console.log("SW registration failed: ", registrationError);
      });
  });
}

/**
 * Export for ES6 modules if needed
 */
if (typeof module !== "undefined" && module.exports) {
  module.exports = PythonMasteryHub;
}
