/**
 * API utility — handles communication with the FastAPI backend.
 *
 * The frontend sends HTTP requests to the backend using axios.
 * The backend runs on port 8000, the frontend on port 5173.
 * CORS middleware on the backend allows this cross-origin request.
 */

import axios from "axios";

const API_BASE = "http://localhost:8000";

/**
 * Send a question to the backend and get an answer.
 *
 * @param {string} question - The user's regulatory question
 * @returns {Object} - { answer, sources, confidence, query_type, verification }
 */
export async function askQuestion(question) {
  const response = await axios.post(`${API_BASE}/api/ask`, {
    question: question,
  });
  return response.data;
}

/**
 * Check if the backend is running.
 *
 * @returns {Object} - { status: "healthy" }
 */
export async function checkHealth() {
  const response = await axios.get(`${API_BASE}/api/health`);
  return response.data;
}
