// Centralized API Client Service with dynamic URL mapping support

const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Perform a fetch request to the API Gateway with centralized base URLs and robust error parses.
 * 
 * @param {string} endpoint - The target endpoint path (e.g. '/api/chat').
 * @param {object} options - Standard fetch options parameter.
 * @returns {Promise<any>} Response JSON data.
 */
export async function apiFetch(endpoint, options = {}) {
  const cleanEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${cleanEndpoint}`;
  
  const defaultHeaders = {
    "Content-Type": "application/json",
  };
  
  const mergedOptions = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  
  const response = await fetch(url, mergedOptions);
  
  if (!response.ok) {
    let errMsg = `HTTP error ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.detail) {
        errMsg = errData.detail;
      }
    } catch (_) {}
    throw new Error(errMsg);
  }
  
  return response.json();
}

export { API_BASE_URL };
