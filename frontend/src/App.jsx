/**
 * App — main component that ties everything together.
 *
 * Layout:
 * ┌─────────────────────────────────────────┐
 * │  Header (title + confidence badge)       │
 * ├────────────────────┬────────────────────┤
 * │                    │                    │
 * │   Chat Window      │   Source Panel     │
 * │   (70% width)      │   (30% width)      │
 * │                    │                    │
 * ├────────────────────┴────────────────────┤
 * │  Chat Input                              │
 * └─────────────────────────────────────────┘
 *
 * State management:
 * - messages: array of {role, content} for the chat history
 * - sources: array of source documents for the latest answer
 * - confidence: latest confidence score (0-1)
 * - queryType: latest query classification
 * - isLoading: whether we're waiting for a response
 */

import { useState, useEffect } from "react";
import { askQuestion, checkHealth } from "./api";
import ChatWindow from "./components/ChatWindow";
import ChatInput from "./components/ChatInput";
import SourcePanel from "./components/SourcePanel";
import ConfidenceBadge from "./components/ConfidenceBadge";

function App() {
  const [messages, setMessages] = useState([]);
  const [sources, setSources] = useState([]);
  const [confidence, setConfidence] = useState(null);
  const [queryType, setQueryType] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState("checking");
  const [showSources, setShowSources] = useState(false);

  // Check if backend is running when the app loads
  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus("connected"))
      .catch(() => setBackendStatus("disconnected"));
  }, []);

  const handleSubmit = async (question) => {
    // Add the user's message to the chat
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsLoading(true);

    try {
      // Call the backend API
      const result = await askQuestion(question);

      // Add the AI's answer to the chat
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer },
      ]);

      // Update the sidebar with sources and confidence
      setSources(result.sources);
      setConfidence(result.confidence);
      setQueryType(result.query_type);
    } catch (error) {
      // If the API call fails, show an error message in the chat
      const errorMsg =
        error.response?.status === 500
          ? "Something went wrong on the server. Please try again."
          : "Could not connect to the backend. Is the server running?";

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errorMsg },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={styles.app}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.title} className="header-title">Regulatory Q&A</h1>
          <span
            style={{
              ...styles.status,
              color: backendStatus === "connected" ? "#22c55e" : "#ef4444",
            }}
          >
            {backendStatus === "connected" ? "Connected" : backendStatus === "checking" ? "Connecting..." : "Disconnected"}
          </span>
        </div>
        <div style={styles.headerRight}>
          {/* Sources toggle button — visible on mobile only */}
          <button
            className="source-toggle"
            style={styles.sourceToggle}
            onClick={() => setShowSources(!showSources)}
          >
            Sources {sources.length > 0 ? `(${sources.length})` : ""}
          </button>
          <div className="confidence-container">
            <ConfidenceBadge confidence={confidence} queryType={queryType} />
          </div>
        </div>
      </header>

      {/* Main content area */}
      <div style={styles.main} className="app-main">
        {/* Left: Chat */}
        <div style={styles.chatSection} className="chat-section">
          <ChatWindow messages={messages} isLoading={isLoading} />
          <ChatInput onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {/* Right: Sources */}
        <div
          style={styles.sourceSection}
          className={`source-section ${showSources ? "visible" : ""}`}
        >
          {/* Close button for mobile overlay */}
          {showSources && (
            <button
              style={styles.closeButton}
              onClick={() => setShowSources(false)}
            >
              Close
            </button>
          )}
          <SourcePanel sources={sources} />
        </div>
      </div>
    </div>
  );
}

const styles = {
  app: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#16161e",
    color: "#e0e0e0",
    fontFamily:
      '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "12px 20px",
    borderBottom: "1px solid #333",
    backgroundColor: "#1a1a2e",
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    gap: "12px",
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
  },
  title: {
    fontSize: "18px",
    fontWeight: 700,
    margin: 0,
  },
  status: {
    fontSize: "11px",
    fontWeight: 500,
  },
  sourceToggle: {
    display: "none",
    alignItems: "center",
    padding: "6px 12px",
    fontSize: "12px",
    fontWeight: 600,
    backgroundColor: "#6366f1",
    color: "#fff",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
  main: {
    flex: 1,
    display: "flex",
    overflow: "hidden",
  },
  chatSection: {
    flex: 7,
    display: "flex",
    flexDirection: "column",
    borderRight: "1px solid #333",
  },
  sourceSection: {
    flex: 3,
    overflow: "hidden",
  },
  closeButton: {
    display: "block",
    width: "100%",
    padding: "12px",
    fontSize: "14px",
    fontWeight: 600,
    backgroundColor: "#6366f1",
    color: "#fff",
    border: "none",
    cursor: "pointer",
  },
};

export default App;
