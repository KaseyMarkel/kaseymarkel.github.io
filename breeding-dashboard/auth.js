/**
 * Authentication and Access Control Module
 * Provides view-only access by default, with GitHub-based editing permissions
 */

class DashboardAuth {
    constructor(config = {}) {
        this.githubToken = config.githubToken || null;
        this.allowedEditors = config.allowedEditors || []; // GitHub usernames
        this.currentUser = null;
        this.permissions = {
            canView: true,
            canEdit: false,
            canExport: false,
            canRefresh: true
        };
    }

    /**
     * Initialize authentication
     */
    async init() {
        // Check if GitHub token exists in localStorage
        const storedToken = localStorage.getItem('github_token');
        if (storedToken) {
            this.githubToken = storedToken;
            await this.verifyGitHubAuth();
        }

        // Everyone can view by default
        this.permissions.canView = true;
        this.permissions.canRefresh = true;

        return this.permissions;
    }

    /**
     * Verify GitHub authentication
     */
    async verifyGitHubAuth() {
        if (!this.githubToken) return false;

        try {
            const response = await fetch('https://api.github.com/user', {
                headers: {
                    'Authorization': `Bearer ${this.githubToken}`,
                    'Accept': 'application/vnd.github.v3+json'
                }
            });

            if (response.ok) {
                const userData = await response.json();
                this.currentUser = userData.login;

                // Check if user is in allowed editors list
                if (this.allowedEditors.includes(this.currentUser)) {
                    this.permissions.canEdit = true;
                    this.permissions.canExport = true;
                }

                return true;
            } else {
                // Invalid token
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('GitHub auth verification failed:', error);
            return false;
        }
    }

    /**
     * Login with GitHub Personal Access Token
     */
    async loginWithGitHub(token) {
        this.githubToken = token;
        localStorage.setItem('github_token', token);

        const success = await this.verifyGitHubAuth();
        if (success) {
            return {
                success: true,
                user: this.currentUser,
                permissions: this.permissions
            };
        } else {
            this.logout();
            return {
                success: false,
                error: 'Invalid GitHub token or authentication failed'
            };
        }
    }

    /**
     * Logout and clear credentials
     */
    logout() {
        this.githubToken = null;
        this.currentUser = null;
        this.permissions.canEdit = false;
        this.permissions.canExport = false;
        localStorage.removeItem('github_token');
    }

    /**
     * Check if current user has specific permission
     */
    can(permission) {
        return this.permissions[permission] || false;
    }

    /**
     * Get current user info
     */
    getCurrentUser() {
        return {
            username: this.currentUser,
            isAuthenticated: !!this.currentUser,
            permissions: this.permissions
        };
    }

    /**
     * Audit log entry for tracking changes
     */
    logAction(action, details = {}) {
        const logEntry = {
            timestamp: new Date().toISOString(),
            user: this.currentUser || 'anonymous',
            action,
            details,
            ip: 'N/A' // Would need server-side implementation
        };

        // Store in localStorage for now (would move to backend)
        const auditLog = JSON.parse(localStorage.getItem('audit_log') || '[]');
        auditLog.push(logEntry);

        // Keep only last 1000 entries
        if (auditLog.length > 1000) {
            auditLog.shift();
        }

        localStorage.setItem('audit_log', JSON.stringify(auditLog));

        return logEntry;
    }

    /**
     * Get audit log
     */
    getAuditLog(limit = 100) {
        const auditLog = JSON.parse(localStorage.getItem('audit_log') || '[]');
        return auditLog.slice(-limit).reverse();
    }
}

/**
 * Access Control UI Component
 */
class AccessControlUI {
    constructor(auth) {
        this.auth = auth;
    }

    /**
     * Render login modal
     */
    renderLoginModal() {
        return `
            <div id="auth-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden">
                <div class="glass-card p-8 max-w-md w-full mx-4">
                    <h2 class="text-2xl font-bold text-gray-800 mb-4">
                        <i class="fas fa-lock mr-2 text-purple-600"></i>
                        Editor Login
                    </h2>
                    <p class="text-gray-600 mb-6">
                        Enter your GitHub Personal Access Token to enable editing permissions.
                        <a href="https://github.com/settings/tokens" target="_blank" class="text-purple-600 hover:underline">
                            Create token
                        </a>
                    </p>
                    <input
                        type="password"
                        id="github-token-input"
                        placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-purple-600"
                    />
                    <div id="auth-error" class="hidden text-red-600 text-sm mb-4"></div>
                    <div class="flex gap-3">
                        <button
                            onclick="closeAuthModal()"
                            class="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onclick="submitGitHubToken()"
                            class="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:shadow-lg transition-all"
                        >
                            Login
                        </button>
                    </div>
                    <p class="text-xs text-gray-500 mt-4">
                        <i class="fas fa-info-circle mr-1"></i>
                        View-only access is always available without login
                    </p>
                </div>
            </div>
        `;
    }

    /**
     * Render user info badge
     */
    renderUserBadge() {
        const user = this.auth.getCurrentUser();

        if (user.isAuthenticated) {
            return `
                <div class="flex items-center gap-3">
                    <div class="flex items-center gap-2 px-4 py-2 bg-green-100 rounded-lg">
                        <i class="fas fa-user-check text-green-600"></i>
                        <span class="text-sm font-medium text-gray-700">${user.username}</span>
                    </div>
                    <button
                        onclick="dashboard.auth.logout(); location.reload();"
                        class="px-3 py-2 text-sm text-gray-600 hover:text-gray-800"
                    >
                        <i class="fas fa-sign-out-alt"></i>
                    </button>
                </div>
            `;
        } else {
            return `
                <button
                    onclick="openAuthModal()"
                    class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
                >
                    <i class="fas fa-user mr-2"></i>
                    Editor Login
                </button>
            `;
        }
    }

    /**
     * Render audit log viewer
     */
    renderAuditLog() {
        const logs = this.auth.getAuditLog(50);

        return `
            <div class="glass-card p-6">
                <h3 class="text-xl font-semibold text-gray-800 mb-4">
                    <i class="fas fa-history mr-2 text-purple-600"></i>
                    Recent Activity
                </h3>
                <div class="space-y-2 max-h-96 overflow-y-auto">
                    ${logs.length === 0 ? '<p class="text-gray-500 text-sm">No activity logged</p>' : ''}
                    ${logs.map(log => `
                        <div class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg text-sm">
                            <span class="text-gray-500">${new Date(log.timestamp).toLocaleString()}</span>
                            <span class="font-medium text-gray-700">${log.user}</span>
                            <span class="text-gray-600">${log.action}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }
}

// Global functions for modal control
window.openAuthModal = () => {
    document.getElementById('auth-modal').classList.remove('hidden');
};

window.closeAuthModal = () => {
    document.getElementById('auth-modal').classList.add('hidden');
    document.getElementById('auth-error').classList.add('hidden');
    document.getElementById('github-token-input').value = '';
};

window.submitGitHubToken = async () => {
    const token = document.getElementById('github-token-input').value.trim();
    const errorDiv = document.getElementById('auth-error');

    if (!token) {
        errorDiv.textContent = 'Please enter a GitHub token';
        errorDiv.classList.remove('hidden');
        return;
    }

    if (window.dashboardAuth) {
        const result = await window.dashboardAuth.loginWithGitHub(token);
        if (result.success) {
            closeAuthModal();
            location.reload();
        } else {
            errorDiv.textContent = result.error;
            errorDiv.classList.remove('hidden');
        }
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { DashboardAuth, AccessControlUI };
}
