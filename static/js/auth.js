/* SkillBridge — shared auth & fetch helpers */

const API = 'http://127.0.0.1:8000';

function getToken() {
  return localStorage.getItem('access_token') || '';
}

function getRefreshToken() {
  return localStorage.getItem('refresh_token') || '';
}

function getUserId() {
  return localStorage.getItem('user_id') || '';
}

function clearAuth() {
  localStorage.clear();
}

/* Fetch wrapper that auto-adds Authorization header and handles 401 */
async function authFetch(url, options = {}) {
  const token = getToken();
  const headers = options.headers || {};

  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, { ...options, headers });

  // If unauthorized on an auth-required page, kick to login
  if (response.status === 401) {
    const isAuthPage = /\/(login|register|forgot_password)/.test(window.location.pathname);
    if (!isAuthPage) {
      clearAuth();
      window.location.href = '/login';
      return response;
    }
  }

  return response;
}

/* Set active nav link based on current path */
(function markActiveNav() {
  document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    document.querySelectorAll('.navbar .nav-links a').forEach(a => {
      const href = a.getAttribute('href');
      if (href && href !== '#' && path.startsWith(href) && href !== '/') {
        a.classList.add('active');
      }
    });
  });
})();