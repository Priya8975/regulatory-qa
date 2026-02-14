/**
 * ChatInput — text field for typing questions.
 *
 * Features:
 * - Submit by pressing Enter or clicking the Send button
 * - Disabled while waiting for a response (prevents double-submit)
 * - Auto-focuses on load so user can start typing immediately
 */

import { useState, useRef, useEffect } from "react";

function ChatInput({ onSubmit, isLoading }) {
  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  // Auto-focus the input when the component loads
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  // Re-focus after loading completes (so user can ask next question)
  useEffect(() => {
    if (!isLoading) {
      inputRef.current?.focus();
    }
  }, [isLoading]);

  const handleSubmit = () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;
    onSubmit(trimmed);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div style={styles.container}>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          isLoading
            ? "Processing..."
            : "Ask a regulatory question..."
        }
        disabled={isLoading}
        style={{
          ...styles.input,
          opacity: isLoading ? 0.6 : 1,
        }}
      />
      <button
        onClick={handleSubmit}
        disabled={isLoading || !input.trim()}
        style={{
          ...styles.button,
          opacity: isLoading || !input.trim() ? 0.5 : 1,
        }}
      >
        {isLoading ? "..." : "Send"}
      </button>
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    gap: "8px",
    padding: "16px",
    borderTop: "1px solid #333",
    backgroundColor: "#1a1a2e",
  },
  input: {
    flex: 1,
    padding: "12px 16px",
    fontSize: "14px",
    backgroundColor: "#2a2a3e",
    border: "1px solid #444",
    borderRadius: "8px",
    color: "#e0e0e0",
    outline: "none",
  },
  button: {
    padding: "12px 24px",
    fontSize: "14px",
    fontWeight: 600,
    backgroundColor: "#6366f1",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    cursor: "pointer",
  },
};

export default ChatInput;
