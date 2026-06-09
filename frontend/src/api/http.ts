import axios, { AxiosError } from "axios";
import { message } from "antd";
import { useAuthStore } from "../stores/authStore";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
});

http.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

http.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ detail?: string; message?: string }>) => {
    const status = error.response?.status;
    const detail = error.response?.data?.detail || error.response?.data?.message || error.message;
    if (status === 401) {
      useAuthStore.getState().clearSession();
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    if (detail && status !== 401) {
      message.error(detail);
    }
    return Promise.reject(error);
  },
);

export function unwrap<T>(request: Promise<{ data: T }>): Promise<T> {
  return request.then((response) => response.data);
}