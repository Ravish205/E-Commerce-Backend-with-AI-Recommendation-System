import axios from "axios";

// Generate or retrieve persistent guest session token
function getSessionToken(): string {
  let token = localStorage.getItem("guest_session_token");
  if (!token) {
    token = "sess_" + Math.random().toString(36).substring(2) + Date.now().toString(36);
    localStorage.setItem("guest_session_token", token);
  }
  return token;
}

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers["X-Session-Token"] = getSessionToken();
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const res = await axios.post("/api/auth/refresh", {}, {
            headers: { Authorization: `Bearer ${refreshToken}` },
          });
          const newToken = res.data.data.access_token;
          localStorage.setItem("access_token", newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        } catch (refreshErr) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          localStorage.removeItem("user");
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
