import axios from "axios";
import { ENV } from "@/config/env";

const apiClient = axios.create({
  baseURL: ENV.API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10s timeout
});

// Request interceptor to append authorization JWT tokens
apiClient.interceptors.request.use(
  (config) => {
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("token");
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to format errors into standard shape
apiClient.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    const errorResponse = {
      success: false,
      error: {
        code: "NETWORK_ERROR",
        message: "An error occurred communicating with the server.",
        details: null,
      },
    };

    if (error.response) {
      // Server responded with an error status code (4xx, 5xx)
      errorResponse.error = error.response.data?.error || {
        code: `HTTP_${error.response.status}`,
        message: error.response.statusText || "Server error occurred.",
        details: error.response.data,
      };
    } else if (error.request) {
      // Request was made but no response was received
      errorResponse.error = {
        code: "TIMEOUT_ERROR",
        message: "The server failed to respond in time.",
        details: null,
      };
    }

    return Promise.reject(errorResponse);
  }
);

export default apiClient;
