// Location: src/python_mastery_hub/web/static/js/auth.js

/**
 * Authentication Handler for Python Mastery Hub
 * Manages user authentication, session management, and security
 */

class AuthManager {
  constructor(options = {}) {
    this.options = {
      tokenKey: "authToken",
      userKey: "userData",
      refreshTokenKey: "refreshToken",
      rememberMeKey: "rememberMe",
      sessionTimeout: 24 * 60 * 60 * 1000, // 24 hours
      autoRefresh: true,
      redirectAfterLogin: "/dashboard",
      redirectAfterLogout: "/",
      enableBiometric: false,
      ...options,
    };

    this.user = null;
    this.token = null;
    this.refreshToken = null;
    this.sessionTimer = null;
    this.refreshTimer = null;
    this.isAuthenticated = false;

    this.init();
  }

  /**
   * Initialize authentication manager
   */
  async init() {
    try {
      this.loadStoredAuth();
      this.setupEventListeners();

      if (this.token) {
        await this.validateSession();
      }

      this.updateUI();
    } catch (error) {
      console.error("Failed to initialize auth manager:", error);
      this.clearAuth();
    }
  }

  /**
   * Load authentication data from storage
   */
  loadStoredAuth() {
    this.token =
      localStorage.getItem(this.options.tokenKey) ||
      sessionStorage.getItem(this.options.tokenKey);

    this.refreshToken = localStorage.getItem(this.options.refreshTokenKey);

    const userData =
      localStorage.getItem(this.options.userKey) ||
      sessionStorage.getItem(this.options.userKey);

    if (userData) {
      try {
        this.user = JSON.parse(userData);
      } catch (error) {
        console.error("Failed to parse user data:", error);
      }
    }

    this.isAuthenticated = !!(this.token && this.user);
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Handle storage changes (multiple tabs)
    window.addEventListener("storage", (event) => {
      if (event.key === this.options.tokenKey) {
        if (event.newValue === null) {
          this.handleLogout();
        } else if (event.newValue !== this.token) {
          this.loadStoredAuth();
          this.updateUI();
        }
      }
    });

    // Handle visibility change for session management
    document.addEventListener("visibilitychange", () => {
      if (!document.hidden && this.isAuthenticated) {
        this.validateSession();
      }
    });

    // Handle network status changes
    window.addEventListener("online", () => {
      if (this.isAuthenticated) {
        this.validateSession();
      }
    });
  }

  /**
   * Login user with credentials
   */
  async login(credentials) {
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Login failed");
      }

      await this.handleLoginSuccess(data, credentials.rememberMe);
      return { success: true, user: this.user };
    } catch (error) {
      console.error("Login error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Register new user
   */
  async register(userData) {
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Registration failed");
      }

      await this.handleLoginSuccess(data, userData.rememberMe);
      return { success: true, user: this.user };
    } catch (error) {
      console.error("Registration error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Handle successful login/registration
   */
  async handleLoginSuccess(data, rememberMe = false) {
    this.token = data.token;
    this.refreshToken = data.refreshToken;
    this.user = data.user;
    this.isAuthenticated = true;

    // Store authentication data
    const storage = rememberMe ? localStorage : sessionStorage;
    storage.setItem(this.options.tokenKey, this.token);
    storage.setItem(this.options.userKey, JSON.stringify(this.user));

    if (this.refreshToken) {
      localStorage.setItem(this.options.refreshTokenKey, this.refreshToken);
    }

    if (rememberMe) {
      localStorage.setItem(this.options.rememberMeKey, "true");
    }

    // Setup session management
    this.setupSessionManagement();

    // Update UI
    this.updateUI();

    // Track login event
    this.trackEvent("user_login", {
      user_id: this.user.id,
      login_method: "credentials",
      remember_me: rememberMe,
    });

    // Redirect if needed
    this.handlePostLoginRedirect();
  }

  /**
   * Logout user
   */
  async logout(redirectToLogin = true) {
    try {
      // Notify server
      if (this.token) {
        await fetch("/api/auth/logout", {
          method: "POST",
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });
      }
    } catch (error) {
      console.error("Logout error:", error);
    }

    this.handleLogout(redirectToLogin);
  }

  /**
   * Handle logout process
   */
  handleLogout(redirectToLogin = true) {
    // Track logout event
    if (this.isAuthenticated) {
      this.trackEvent("user_logout", {
        user_id: this.user?.id,
      });
    }

    // Clear authentication data
    this.clearAuth();

    // Clear session timers
    this.clearSessionManagement();

    // Update UI
    this.updateUI();

    // Redirect if needed
    if (redirectToLogin) {
      this.redirectToLogin();
    }
  }

  /**
   * Clear all authentication data
   */
  clearAuth() {
    this.token = null;
    this.refreshToken = null;
    this.user = null;
    this.isAuthenticated = false;

    // Clear from storage
    localStorage.removeItem(this.options.tokenKey);
    localStorage.removeItem(this.options.userKey);
    localStorage.removeItem(this.options.refreshTokenKey);
    localStorage.removeItem(this.options.rememberMeKey);
    sessionStorage.removeItem(this.options.tokenKey);
    sessionStorage.removeItem(this.options.userKey);
  }

  /**
   * Validate current session
   */
  async validateSession() {
    if (!this.token) return false;

    try {
      const response = await fetch("/api/auth/validate", {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.user) {
          this.user = data.user;
          this.updateStoredUser();
        }
        return true;
      } else {
        // Token is invalid, try to refresh
        if (this.refreshToken && this.options.autoRefresh) {
          return await this.refreshAuthToken();
        } else {
          this.handleLogout();
          return false;
        }
      }
    } catch (error) {
      console.error("Session validation error:", error);
      return false;
    }
  }

  /**
   * Refresh authentication token
   */
  async refreshAuthToken() {
    if (!this.refreshToken) return false;

    try {
      const response = await fetch("/api/auth/refresh", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          refreshToken: this.refreshToken,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.token;

        // Update stored token
        const storage = localStorage.getItem(this.options.rememberMeKey)
          ? localStorage
          : sessionStorage;
        storage.setItem(this.options.tokenKey, this.token);

        return true;
      } else {
        this.handleLogout();
        return false;
      }
    } catch (error) {
      console.error("Token refresh error:", error);
      this.handleLogout();
      return false;
    }
  }

  /**
   * Setup session management timers
   */
  setupSessionManagement() {
    this.clearSessionManagement();

    // Setup auto-refresh timer
    if (this.options.autoRefresh && this.refreshToken) {
      this.refreshTimer = setInterval(() => {
        this.refreshAuthToken();
      }, 55 * 60 * 1000); // Refresh every 55 minutes
    }

    // Setup session timeout
    this.sessionTimer = setTimeout(() => {
      this.handleSessionTimeout();
    }, this.options.sessionTimeout);
  }

  /**
   * Clear session management timers
   */
  clearSessionManagement() {
    if (this.sessionTimer) {
      clearTimeout(this.sessionTimer);
      this.sessionTimer = null;
    }

    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }

  /**
   * Handle session timeout
   */
  handleSessionTimeout() {
    this.showSessionTimeoutWarning();
  }

  /**
   * Show session timeout warning
   */
  showSessionTimeoutWarning() {
    const modal = document.createElement("div");
    modal.className = "session-timeout-modal";
    modal.innerHTML = `
            <div class="session-timeout-content">
                <h3>Session Timeout Warning</h3>
                <p>Your session is about to expire. Would you like to continue?</p>
                <div class="session-timeout-actions">
                    <button onclick="authManager.extendSession()" class="btn btn-primary">
                        Continue Session
                    </button>
                    <button onclick="authManager.logout()" class="btn btn-secondary">
                        Logout
                    </button>
                </div>
            </div>
        `;

    document.body.appendChild(modal);

    // Auto-logout after 2 minutes if no action
    setTimeout(() => {
      if (modal.parentNode) {
        this.logout();
      }
    }, 2 * 60 * 1000);
  }

  /**
   * Extend current session
   */
  async extendSession() {
    const modal = document.querySelector(".session-timeout-modal");
    if (modal) {
      modal.remove();
    }

    const isValid = await this.validateSession();
    if (isValid) {
      this.setupSessionManagement();
    } else {
      this.logout();
    }
  }

  /**
   * Social authentication (Google, GitHub, etc.)
   */
  async socialAuth(provider) {
    try {
      // Open popup for social auth
      const popup = window.open(
        `/api/auth/${provider}`,
        "socialAuth",
        "width=600,height=600,scrollbars=yes,resizable=yes"
      );

      // Listen for popup messages
      return new Promise((resolve, reject) => {
        const messageHandler = (event) => {
          if (event.origin !== window.location.origin) return;

          if (event.data.type === "SOCIAL_AUTH_SUCCESS") {
            window.removeEventListener("message", messageHandler);
            popup.close();
            this.handleLoginSuccess(event.data.authData, true);
            resolve({ success: true });
          } else if (event.data.type === "SOCIAL_AUTH_ERROR") {
            window.removeEventListener("message", messageHandler);
            popup.close();
            reject(new Error(event.data.error));
          }
        };

        window.addEventListener("message", messageHandler);

        // Handle popup close
        const checkClosed = setInterval(() => {
          if (popup.closed) {
            clearInterval(checkClosed);
            window.removeEventListener("message", messageHandler);
            reject(new Error("Authentication cancelled"));
          }
        }, 1000);
      });
    } catch (error) {
      console.error("Social auth error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Password reset request
   */
  async requestPasswordReset(email) {
    try {
      const response = await fetch("/api/auth/password-reset", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      return { success: response.ok, message: data.message };
    } catch (error) {
      console.error("Password reset error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Reset password with token
   */
  async resetPassword(token, newPassword) {
    try {
      const response = await fetch("/api/auth/password-reset/confirm", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ token, password: newPassword }),
      });

      const data = await response.json();
      return { success: response.ok, message: data.message };
    } catch (error) {
      console.error("Password reset confirmation error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Change password for authenticated user
   */
  async changePassword(currentPassword, newPassword) {
    if (!this.isAuthenticated) {
      throw new Error("User not authenticated");
    }

    try {
      const response = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.token}`,
        },
        body: JSON.stringify({
          currentPassword,
          newPassword,
        }),
      });

      const data = await response.json();
      return { success: response.ok, message: data.message };
    } catch (error) {
      console.error("Password change error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Enable two-factor authentication
   */
  async enableTwoFactor() {
    if (!this.isAuthenticated) {
      throw new Error("User not authenticated");
    }

    try {
      const response = await fetch("/api/auth/2fa/enable", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      const data = await response.json();
      return { success: response.ok, data };
    } catch (error) {
      console.error("2FA enable error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Verify two-factor authentication code
   */
  async verifyTwoFactor(code) {
    try {
      const response = await fetch("/api/auth/2fa/verify", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.token}`,
        },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();
      return { success: response.ok, data };
    } catch (error) {
      console.error("2FA verification error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Get user profile
   */
  async getUserProfile() {
    if (!this.isAuthenticated) return null;

    try {
      const response = await fetch("/api/user/profile", {
        headers: {
          Authorization: `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        this.user = userData;
        this.updateStoredUser();
        return userData;
      }
    } catch (error) {
      console.error("Failed to get user profile:", error);
    }

    return null;
  }

  /**
   * Update user profile
   */
  async updateUserProfile(profileData) {
    if (!this.isAuthenticated) {
      throw new Error("User not authenticated");
    }

    try {
      const response = await fetch("/api/user/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${this.token}`,
        },
        body: JSON.stringify(profileData),
      });

      const data = await response.json();

      if (response.ok) {
        this.user = { ...this.user, ...data.user };
        this.updateStoredUser();
      }

      return { success: response.ok, data };
    } catch (error) {
      console.error("Profile update error:", error);
      return { success: false, error: error.message };
    }
  }

  /**
   * Update stored user data
   */
  updateStoredUser() {
    const storage = localStorage.getItem(this.options.rememberMeKey)
      ? localStorage
      : sessionStorage;
    storage.setItem(this.options.userKey, JSON.stringify(this.user));
  }

  /**
   * Check if user has specific permission
   */
  hasPermission(permission) {
    return this.user?.permissions?.includes(permission) || false;
  }

  /**
   * Check if user has specific role
   */
  hasRole(role) {
    return this.user?.roles?.includes(role) || false;
  }

  /**
   * Get authentication header for API requests
   */
  getAuthHeader() {
    return this.token ? { Authorization: `Bearer ${this.token}` } : {};
  }

  /**
   * Make authenticated API request
   */
  async authenticatedFetch(url, options = {}) {
    const headers = {
      ...options.headers,
      ...this.getAuthHeader(),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle token expiration
    if (response.status === 401) {
      if (this.options.autoRefresh && this.refreshToken) {
        const refreshed = await this.refreshAuthToken();
        if (refreshed) {
          // Retry with new token
          headers.Authorization = `Bearer ${this.token}`;
          return fetch(url, { ...options, headers });
        }
      }
      this.handleLogout();
    }

    return response;
  }

  /**
   * Update UI based on authentication state
   */
  updateUI() {
    // Update user display elements
    const userElements = document.querySelectorAll("[data-user-info]");
    userElements.forEach((element) => {
      const info = element.dataset.userInfo;
      if (this.user && this.user[info]) {
        element.textContent = this.user[info];
      }
    });

    // Show/hide authenticated content
    const authElements = document.querySelectorAll(
      '[data-auth-required="true"]'
    );
    authElements.forEach((element) => {
      element.style.display = this.isAuthenticated ? "" : "none";
    });

    const noAuthElements = document.querySelectorAll(
      '[data-auth-required="false"]'
    );
    noAuthElements.forEach((element) => {
      element.style.display = this.isAuthenticated ? "none" : "";
    });

    // Update navigation
    this.updateNavigation();

    // Dispatch auth state change event
    document.dispatchEvent(
      new CustomEvent("authStateChanged", {
        detail: {
          isAuthenticated: this.isAuthenticated,
          user: this.user,
        },
      })
    );
  }

  /**
   * Update navigation based on auth state
   */
  updateNavigation() {
    const loginLinks = document.querySelectorAll(".login-link");
    const logoutLinks = document.querySelectorAll(".logout-link");
    const userMenu = document.querySelector(".user-menu");

    if (this.isAuthenticated) {
      loginLinks.forEach((link) => (link.style.display = "none"));
      logoutLinks.forEach((link) => (link.style.display = ""));
      if (userMenu) userMenu.style.display = "";
    } else {
      loginLinks.forEach((link) => (link.style.display = ""));
      logoutLinks.forEach((link) => (link.style.display = "none"));
      if (userMenu) userMenu.style.display = "none";
    }
  }

  /**
   * Handle post-login redirect
   */
  handlePostLoginRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    const redirect =
      urlParams.get("redirect") || this.options.redirectAfterLogin;

    if (redirect && redirect !== window.location.pathname) {
      window.location.href = redirect;
    }
  }

  /**
   * Redirect to login page
   */
  redirectToLogin() {
    const currentPath = window.location.pathname;
    const loginUrl = `/login?redirect=${encodeURIComponent(currentPath)}`;
    window.location.href = loginUrl;
  }

  /**
   * Track authentication events
   */
  trackEvent(eventName, data) {
    if (window.progressTracker) {
      window.progressTracker.trackEvent(eventName, data);
    }
  }

  /**
   * Dispose of auth manager
   */
  dispose() {
    this.clearSessionManagement();
  }
}

// Create global auth manager instance
window.authManager = new AuthManager();

// Auto-setup form handlers
document.addEventListener("DOMContentLoaded", () => {
  // Login form handler
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(loginForm);
      const credentials = {
        email: formData.get("email"),
        password: formData.get("password"),
        rememberMe: formData.get("rememberMe") === "on",
      };

      const result = await window.authManager.login(credentials);
      if (!result.success) {
        // Show error message
        console.error("Login failed:", result.error);
      }
    });
  }

  // Register form handler
  const registerForm = document.getElementById("registerForm");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(registerForm);
      const userData = Object.fromEntries(formData);

      const result = await window.authManager.register(userData);
      if (!result.success) {
        // Show error message
        console.error("Registration failed:", result.error);
      }
    });
  }

  // Logout link handlers
  document.querySelectorAll(".logout-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      window.authManager.logout();
    });
  });
});
