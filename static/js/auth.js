const API = 'http://127.0.0.1:8000';

function getToken()        { return localStorage.getItem('access_token'); }
function getRefreshToken() { return localStorage.getItem('refresh_token'); }
function getUserId()       { return localStorage.getItem('user_id'); }

function redirectToLogin() {
  localStorage.clear();
  window.location.href = '/login';
}

async function tryRefresh() {
  const rt = getRefreshToken();
  if (!rt) return false;
  try {
    const res = await fetch(`${API}/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: rt })
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return true;
  } catch { return false; }
}

/**
 * Drop-in replacement for fetch() that:
 *  - Adds Authorization header automatically
 *  - On 401, tries to refresh the token once and retries
 *  - If refresh fails, redirects to /login
 */
async function authFetch(url, options = {}) {
  options.headers = options.headers || {};
  options.headers['Authorization'] = `Bearer ${getToken()}`;

  let res = await fetch(url, options);

  if (res.status === 401) {
    const refreshed = await tryRefresh();
    if (!refreshed) { redirectToLogin(); return res; }
    options.headers['Authorization'] = `Bearer ${getToken()}`;
    res = await fetch(url, options);
    if (res.status === 401) { redirectToLogin(); return res; }
  }

  return res;
}
