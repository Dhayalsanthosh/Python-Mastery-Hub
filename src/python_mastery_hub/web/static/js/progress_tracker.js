// Location: src/python_mastery_hub/web/static/js/progress_tracker.js

/**
 * Progress Tracker for Python Mastery Hub
 * Handles user progress tracking, analytics, and achievement management
 */

class ProgressTracker {
  constructor(options = {}) {
    this.options = {
      autoSync: true,
      syncInterval: 30000, // 30 seconds
      enableAchievements: true,
      enableStreakTracking: true,
      enableAnalytics: true,
      cacheData: true,
      ...options,
    };

    this.data = {
      user: null,
      progress: {},
      achievements: [],
      streak: 0,
      sessionData: {},
      analytics: {
        events: [],
        timeSpent: {},
        exerciseStats: {},
      },
    };

    this.cache = new Map();
    this.syncTimer = null;
    this.sessionStartTime = Date.now();
    this.lastActivity = Date.now();

    this.init();
  }

  /**
   * Initialize the progress tracker
   */
  async init() {
    try {
      await this.loadUserData();
      await this.loadProgress();
      this.setupEventListeners();
      this.startSession();

      if (this.options.autoSync) {
        this.startAutoSync();
      }
    } catch (error) {
      console.error("Failed to initialize progress tracker:", error);
    }
  }

  /**
   * Load user data
   */
  async loadUserData() {
    try {
      const response = await fetch("/api/user/profile", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      });

      if (response.ok) {
        this.data.user = await response.json();
      }
    } catch (error) {
      console.error("Failed to load user data:", error);
    }
  }

  /**
   * Load progress data
   */
  async loadProgress() {
    try {
      // Load from cache first
      if (this.options.cacheData) {
        this.loadFromCache();
      }

      // Then load from server
      const response = await fetch("/api/progress", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
      });

      if (response.ok) {
        const progressData = await response.json();
        this.data.progress = progressData.progress || {};
        this.data.achievements = progressData.achievements || [];
        this.data.streak = progressData.streak || 0;

        if (this.options.cacheData) {
          this.saveToCache();
        }
      }
    } catch (error) {
      console.error("Failed to load progress:", error);
    }
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Track user activity
    ["click", "keypress", "scroll", "mousemove"].forEach((event) => {
      document.addEventListener(
        event,
        () => {
          this.lastActivity = Date.now();
        },
        { passive: true }
      );
    });

    // Track page visibility
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        this.pauseSession();
      } else {
        this.resumeSession();
      }
    });

    // Track page unload
    window.addEventListener("beforeunload", () => {
      this.endSession();
    });

    // Track exercise events
    document.addEventListener("exerciseStarted", (event) => {
      this.trackExerciseStart(event.detail);
    });

    document.addEventListener("exerciseCompleted", (event) => {
      this.trackExerciseCompletion(event.detail);
    });

    document.addEventListener("achievementUnlocked", (event) => {
      this.handleAchievementUnlocked(event.detail);
    });
  }

  /**
   * Start tracking session
   */
  startSession() {
    this.data.sessionData = {
      startTime: this.sessionStartTime,
      endTime: null,
      timeSpent: 0,
      exercisesAttempted: 0,
      exercisesCompleted: 0,
      hintsUsed: 0,
      testsRun: 0,
      codeExecutions: 0,
    };

    this.trackEvent("session_started", {
      timestamp: this.sessionStartTime,
      user_agent: navigator.userAgent,
      screen_resolution: `${screen.width}x${screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    });
  }

  /**
   * Pause session tracking
   */
  pauseSession() {
    if (this.data.sessionData.endTime) return; // Already paused

    this.data.sessionData.timeSpent += Date.now() - this.lastActivity;
    this.trackEvent("session_paused", {
      timeSpent: this.data.sessionData.timeSpent,
    });
  }

  /**
   * Resume session tracking
   */
  resumeSession() {
    this.lastActivity = Date.now();
    this.trackEvent("session_resumed", {
      timeSpent: this.data.sessionData.timeSpent,
    });
  }

  /**
   * End session tracking
   */
  endSession() {
    if (this.data.sessionData.endTime) return; // Already ended

    this.data.sessionData.endTime = Date.now();
    this.data.sessionData.timeSpent +=
      this.data.sessionData.endTime - this.lastActivity;

    this.trackEvent("session_ended", {
      totalTime: this.data.sessionData.timeSpent,
      exercisesAttempted: this.data.sessionData.exercisesAttempted,
      exercisesCompleted: this.data.sessionData.exercisesCompleted,
    });

    this.syncProgress();
  }

  /**
   * Track exercise start
   */
  trackExerciseStart(data) {
    this.data.sessionData.exercisesAttempted++;

    this.trackEvent("exercise_started", {
      exercise_id: data.exercise_id,
      difficulty: data.difficulty,
      topic: data.topic,
    });

    // Initialize exercise progress if not exists
    if (!this.data.progress[data.exercise_id]) {
      this.data.progress[data.exercise_id] = {
        status: "in_progress",
        attempts: 0,
        time_spent: 0,
        hints_used: 0,
        best_score: 0,
        first_attempt: Date.now(),
        last_attempt: Date.now(),
      };
    }

    this.data.progress[data.exercise_id].attempts++;
    this.data.progress[data.exercise_id].last_attempt = Date.now();
  }

  /**
   * Track exercise completion
   */
  trackExerciseCompletion(data) {
    this.data.sessionData.exercisesCompleted++;

    const exerciseId = data.exercise_id;
    const progress = this.data.progress[exerciseId];

    if (progress) {
      progress.status = "completed";
      progress.best_score = Math.max(progress.best_score, data.score || 0);
      progress.time_spent += data.time_taken || 0;
      progress.completed_at = Date.now();
    }

    this.trackEvent("exercise_completed", {
      exercise_id: exerciseId,
      score: data.score,
      time_taken: data.time_taken,
      attempts: progress?.attempts || 1,
      hints_used: data.hints_used || 0,
    });

    // Check for achievements
    if (this.options.enableAchievements) {
      this.checkAchievements(data);
    }

    // Update streak
    if (this.options.enableStreakTracking) {
      this.updateStreak();
    }

    this.syncProgress();
  }

  /**
   * Update learning streak
   */
  updateStreak() {
    const today = new Date().toDateString();
    const lastActivityDate = localStorage.getItem("lastActivityDate");

    if (lastActivityDate === today) {
      // Already counted today
      return;
    }

    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

    if (lastActivityDate === yesterday.toDateString()) {
      // Consecutive day
      this.data.streak++;
    } else if (lastActivityDate !== today) {
      // Streak broken
      this.data.streak = 1;
    }

    localStorage.setItem("lastActivityDate", today);

    this.trackEvent("streak_updated", {
      streak: this.data.streak,
      date: today,
    });

    // Trigger streak achievement check
    this.checkStreakAchievements();
  }

  /**
   * Check for new achievements
   */
  async checkAchievements(data) {
    const completedExercises = Object.values(this.data.progress).filter(
      (p) => p.status === "completed"
    ).length;

    const totalScore = Object.values(this.data.progress).reduce(
      (sum, p) => sum + (p.best_score || 0),
      0
    );

    const achievements = [
      {
        id: "first_exercise",
        condition: completedExercises >= 1,
        title: "First Steps",
        description: "Complete your first exercise",
      },
      {
        id: "ten_exercises",
        condition: completedExercises >= 10,
        title: "Getting Started",
        description: "Complete 10 exercises",
      },
      {
        id: "fifty_exercises",
        condition: completedExercises >= 50,
        title: "Dedicated Learner",
        description: "Complete 50 exercises",
      },
      {
        id: "hundred_exercises",
        condition: completedExercises >= 100,
        title: "Python Expert",
        description: "Complete 100 exercises",
      },
      {
        id: "perfect_score",
        condition: data.score === 100,
        title: "Perfect Score",
        description: "Get 100% on an exercise",
      },
      {
        id: "high_scorer",
        condition: totalScore >= 5000,
        title: "High Scorer",
        description: "Earn 5000 total points",
      },
    ];

    for (const achievement of achievements) {
      if (achievement.condition && !this.hasAchievement(achievement.id)) {
        await this.unlockAchievement(achievement);
      }
    }
  }

  /**
   * Check for streak achievements
   */
  checkStreakAchievements() {
    const streakAchievements = [
      {
        id: "streak_3",
        days: 3,
        title: "3-Day Streak",
        description: "Learn for 3 consecutive days",
      },
      {
        id: "streak_7",
        days: 7,
        title: "Week Warrior",
        description: "Learn for 7 consecutive days",
      },
      {
        id: "streak_30",
        days: 30,
        title: "Month Master",
        description: "Learn for 30 consecutive days",
      },
      {
        id: "streak_100",
        days: 100,
        title: "Century Achiever",
        description: "Learn for 100 consecutive days",
      },
    ];

    for (const achievement of streakAchievements) {
      if (
        this.data.streak >= achievement.days &&
        !this.hasAchievement(achievement.id)
      ) {
        this.unlockAchievement(achievement);
      }
    }
  }

  /**
   * Check if user has specific achievement
   */
  hasAchievement(achievementId) {
    return this.data.achievements.some((a) => a.id === achievementId);
  }

  /**
   * Unlock new achievement
   */
  async unlockAchievement(achievement) {
    achievement.unlocked_at = Date.now();
    this.data.achievements.push(achievement);

    // Notify server
    try {
      await fetch("/api/achievements/unlock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify(achievement),
      });
    } catch (error) {
      console.error("Failed to unlock achievement on server:", error);
    }

    // Trigger UI notification
    this.showAchievementNotification(achievement);

    // Emit custom event
    document.dispatchEvent(
      new CustomEvent("achievementUnlocked", {
        detail: achievement,
      })
    );

    this.trackEvent("achievement_unlocked", {
      achievement_id: achievement.id,
      title: achievement.title,
    });
  }

  /**
   * Handle achievement unlocked event
   */
  handleAchievementUnlocked(achievement) {
    this.showAchievementNotification(achievement);
  }

  /**
   * Show achievement notification
   */
  showAchievementNotification(achievement) {
    const notification = document.createElement("div");
    notification.className = "achievement-notification";
    notification.innerHTML = `
            <div class="achievement-content">
                <div class="achievement-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <div class="achievement-text">
                    <h4>Achievement Unlocked!</h4>
                    <h5>${achievement.title}</h5>
                    <p>${achievement.description}</p>
                </div>
                <button class="close-achievement" onclick="this.closest('.achievement-notification').remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

    document.body.appendChild(notification);

    // Auto-remove after 8 seconds
    setTimeout(() => {
      if (notification.parentNode) {
        notification.remove();
      }
    }, 8000);

    // Add confetti effect if available
    if (typeof confetti !== "undefined") {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    }
  }

  /**
   * Track analytics event
   */
  trackEvent(eventName, data = {}) {
    if (!this.options.enableAnalytics) return;

    const event = {
      name: eventName,
      data: data,
      timestamp: Date.now(),
      session_id: this.sessionStartTime,
      user_id: this.data.user?.id,
    };

    this.data.analytics.events.push(event);

    // Send to server if queue is getting full
    if (this.data.analytics.events.length >= 10) {
      this.flushAnalytics();
    }
  }

  /**
   * Flush analytics events to server
   */
  async flushAnalytics() {
    if (!this.data.analytics.events.length) return;

    try {
      await fetch("/api/analytics/events", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          events: this.data.analytics.events,
        }),
      });

      this.data.analytics.events = [];
    } catch (error) {
      console.error("Failed to send analytics:", error);
    }
  }

  /**
   * Start auto-sync timer
   */
  startAutoSync() {
    this.syncTimer = setInterval(() => {
      this.syncProgress();
    }, this.options.syncInterval);
  }

  /**
   * Stop auto-sync timer
   */
  stopAutoSync() {
    if (this.syncTimer) {
      clearInterval(this.syncTimer);
      this.syncTimer = null;
    }
  }

  /**
   * Sync progress with server
   */
  async syncProgress() {
    try {
      const response = await fetch("/api/progress/sync", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          progress: this.data.progress,
          achievements: this.data.achievements,
          streak: this.data.streak,
          session_data: this.data.sessionData,
          analytics: this.data.analytics,
        }),
      });

      if (response.ok) {
        const result = await response.json();

        // Update with server data if newer
        if (result.updated_progress) {
          this.data.progress = {
            ...this.data.progress,
            ...result.updated_progress,
          };
        }

        // Clear synced analytics
        this.data.analytics.events = [];

        if (this.options.cacheData) {
          this.saveToCache();
        }
      }
    } catch (error) {
      console.error("Failed to sync progress:", error);
    }
  }

  /**
   * Get exercise progress
   */
  getExerciseProgress(exerciseId) {
    return (
      this.data.progress[exerciseId] || {
        status: "not_started",
        attempts: 0,
        time_spent: 0,
        hints_used: 0,
        best_score: 0,
      }
    );
  }

  /**
   * Get overall progress statistics
   */
  getOverallProgress() {
    const exercises = Object.values(this.data.progress);
    const completed = exercises.filter((e) => e.status === "completed");

    return {
      total_exercises: exercises.length,
      completed_exercises: completed.length,
      completion_rate: exercises.length
        ? (completed.length / exercises.length) * 100
        : 0,
      total_time: exercises.reduce((sum, e) => sum + e.time_spent, 0),
      average_score: completed.length
        ? completed.reduce((sum, e) => sum + e.best_score, 0) / completed.length
        : 0,
      streak: this.data.streak,
      achievements_count: this.data.achievements.length,
    };
  }

  /**
   * Get learning analytics
   */
  getLearningAnalytics(timeframe = "7d") {
    const now = Date.now();
    const timeframes = {
      "1d": 24 * 60 * 60 * 1000,
      "7d": 7 * 24 * 60 * 60 * 1000,
      "30d": 30 * 24 * 60 * 60 * 1000,
      "90d": 90 * 24 * 60 * 60 * 1000,
    };

    const cutoff = now - timeframes[timeframe];
    const recentEvents = this.data.analytics.events.filter(
      (e) => e.timestamp >= cutoff
    );

    return {
      total_events: recentEvents.length,
      exercise_completions: recentEvents.filter(
        (e) => e.name === "exercise_completed"
      ).length,
      time_spent: this.data.sessionData.timeSpent,
      average_session_time: this.calculateAverageSessionTime(recentEvents),
      most_active_topics: this.getMostActiveTopics(recentEvents),
      learning_velocity: this.calculateLearningVelocity(recentEvents),
    };
  }

  /**
   * Calculate average session time
   */
  calculateAverageSessionTime(events) {
    const sessions = events.filter((e) => e.name === "session_ended");
    if (!sessions.length) return 0;

    const totalTime = sessions.reduce(
      (sum, s) => sum + (s.data.totalTime || 0),
      0
    );
    return totalTime / sessions.length;
  }

  /**
   * Get most active topics
   */
  getMostActiveTopics(events) {
    const topicCounts = {};

    events
      .filter((e) => e.name === "exercise_completed")
      .forEach((event) => {
        const topic = event.data.topic;
        if (topic) {
          topicCounts[topic] = (topicCounts[topic] || 0) + 1;
        }
      });

    return Object.entries(topicCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([topic, count]) => ({ topic, count }));
  }

  /**
   * Calculate learning velocity (exercises per day)
   */
  calculateLearningVelocity(events) {
    const completions = events.filter((e) => e.name === "exercise_completed");
    if (!completions.length) return 0;

    const daySpan =
      (Date.now() - completions[completions.length - 1].timestamp) /
      (24 * 60 * 60 * 1000);
    return daySpan > 0 ? completions.length / daySpan : 0;
  }

  /**
   * Save data to cache
   */
  saveToCache() {
    const cacheData = {
      progress: this.data.progress,
      achievements: this.data.achievements,
      streak: this.data.streak,
      timestamp: Date.now(),
    };

    localStorage.setItem("progress_cache", JSON.stringify(cacheData));
  }

  /**
   * Load data from cache
   */
  loadFromCache() {
    try {
      const cached = localStorage.getItem("progress_cache");
      if (cached) {
        const data = JSON.parse(cached);

        // Only use cache if it's less than 1 hour old
        if (Date.now() - data.timestamp < 60 * 60 * 1000) {
          this.data.progress = data.progress || {};
          this.data.achievements = data.achievements || [];
          this.data.streak = data.streak || 0;
        }
      }
    } catch (error) {
      console.error("Failed to load from cache:", error);
    }
  }

  /**
   * Clear cache
   */
  clearCache() {
    localStorage.removeItem("progress_cache");
  }

  /**
   * Export progress data
   */
  exportProgress() {
    const exportData = {
      user: this.data.user,
      progress: this.data.progress,
      achievements: this.data.achievements,
      streak: this.data.streak,
      analytics: this.getLearningAnalytics("90d"),
      exported_at: Date.now(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `progress_export_${
      new Date().toISOString().split("T")[0]
    }.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * Reset progress (with confirmation)
   */
  resetProgress() {
    const confirmation = confirm(
      "Are you sure you want to reset all progress? This cannot be undone."
    );
    if (!confirmation) return;

    const doubleConfirmation = confirm(
      "This will permanently delete all your progress, achievements, and statistics. Are you absolutely sure?"
    );
    if (!doubleConfirmation) return;

    this.data.progress = {};
    this.data.achievements = [];
    this.data.streak = 0;
    this.data.analytics = { events: [], timeSpent: {}, exerciseStats: {} };

    this.clearCache();
    this.syncProgress();

    this.trackEvent("progress_reset", {
      timestamp: Date.now(),
    });
  }

  /**
   * Get recommendations based on progress
   */
  getRecommendations() {
    const progress = this.getOverallProgress();
    const analytics = this.getLearningAnalytics("7d");

    const recommendations = [];

    // Streak recommendations
    if (this.data.streak === 0) {
      recommendations.push({
        type: "streak",
        title: "Start Your Learning Streak",
        description:
          "Complete an exercise today to start building a learning habit.",
        action: "Browse Exercises",
        url: "/exercises",
      });
    } else if (this.data.streak < 7) {
      recommendations.push({
        type: "streak",
        title: "Keep Your Streak Going",
        description: `You're on a ${this.data.streak}-day streak! Don't break it now.`,
        action: "Practice Today",
        url: "/exercises",
      });
    }

    // Progress recommendations
    if (progress.completion_rate < 50 && progress.total_exercises > 5) {
      recommendations.push({
        type: "progress",
        title: "Focus on Completion",
        description: "Try finishing more exercises to build confidence.",
        action: "Retry Incomplete",
        url: "/exercises?status=in-progress",
      });
    }

    // Topic recommendations
    if (analytics.most_active_topics.length > 0) {
      const leastActive = this.getLeastActiveTopics();
      if (leastActive.length > 0) {
        recommendations.push({
          type: "variety",
          title: "Explore New Topics",
          description: `Try ${leastActive[0]} exercises to broaden your skills.`,
          action: "Explore Topic",
          url: `/exercises?topic=${leastActive[0]}`,
        });
      }
    }

    return recommendations;
  }

  /**
   * Get least active topics for recommendations
   */
  getLeastActiveTopics() {
    const allTopics = [
      "basics",
      "data-structures",
      "algorithms",
      "oop",
      "web",
      "data-science",
    ];
    const analytics = this.getLearningAnalytics("30d");
    const activeTopics = analytics.most_active_topics.map((t) => t.topic);

    return allTopics.filter((topic) => !activeTopics.includes(topic));
  }

  /**
   * Dispose of the progress tracker
   */
  dispose() {
    this.stopAutoSync();
    this.endSession();
    this.flushAnalytics();
  }
}

// Export for global use
window.ProgressTracker = ProgressTracker;

// Global instance
window.progressTracker = new ProgressTracker();

// Auto-initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Additional initialization if needed
});
