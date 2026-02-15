/**
 * ChatWindow — displays the conversation between user and AI.
 *
 * Messages are displayed as chat bubbles:
 * - User messages: right-aligned, purple
 * - AI answers: left-aligned, dark gray, with markdown-like formatting
 *
 * Auto-scrolls to the latest message when new ones are added.
 */

import { useEffect, useRef } from "react";

function ChatWindow({ messages, isLoading }) {
  const bottomRef = useRef(null);

  // Auto-scroll to bottom whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div style={styles.emptyState}>
        <h2 style={styles.emptyTitle}>Regulatory Q&A</h2>
        <p style={styles.emptyText}>
          Ask questions about regulatory frameworks like SR 11-7,
          NIST AI RMF, ISO 42001, and more.
        </p>
        <div style={styles.examples}>
          <p style={styles.exampleLabel}>Try asking:</p>
          <p style={styles.example}>
            "What does SR 11-7 require for model validation?"
          </p>
          <p style={styles.example}>
            "How do SR 11-7 and NIST AI RMF differ on risk assessment?"
          </p>
          <p style={styles.example}>
            "Explain the concept of effective challenge"
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container} className="chat-messages">
      {messages.map((msg, index) => (
        <div
          key={index}
          style={{
            ...styles.messageRow,
            justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
          }}
        >
          <div
            style={{
              ...styles.bubble,
              ...(msg.role === "user" ? styles.userBubble : styles.aiBubble),
            }}
          >
            {msg.role === "assistant" ? (
              <div
                style={styles.aiText}
                dangerouslySetInnerHTML={{
                  __html: formatAnswer(msg.content),
                }}
              />
            ) : (
              <span>{msg.content}</span>
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div style={{ ...styles.messageRow, justifyContent: "flex-start" }}>
          <div style={{ ...styles.bubble, ...styles.aiBubble }}>
            <div style={styles.loadingDots}>
              <span style={styles.dot}>.</span>
              <span style={{ ...styles.dot, animationDelay: "0.2s" }}>.</span>
              <span style={{ ...styles.dot, animationDelay: "0.4s" }}>.</span>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}

/**
 * Simple formatter to make the AI's answer more readable.
 * Converts markdown-like patterns to HTML:
 * - **bold** -> <strong>bold</strong>
 * - Numbered lists (1. item) -> styled list items
 * - [Source: ...] citations -> highlighted spans
 */
function formatAnswer(text) {
  let html = text
    // Escape HTML to prevent XSS
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Bold text: **text** -> <strong>text</strong>
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    // Citations: [Source: ...] -> highlighted
    .replace(
      /\[Source:([^\]]+)\]/g,
      '<span style="color: #818cf8; font-size: 12px;">[Source:$1]</span>'
    )
    // Line breaks
    .replace(/\n/g, "<br/>");

  return html;
}

const styles = {
  container: {
    flex: 1,
    overflowY: "auto",
    padding: "16px",
    display: "flex",
    flexDirection: "column",
    gap: "12px",
    minHeight: 0,
    WebkitOverflowScrolling: "touch",
  },
  emptyState: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    padding: "40px",
    color: "#888",
  },
  emptyTitle: {
    fontSize: "24px",
    color: "#e0e0e0",
    marginBottom: "8px",
  },
  emptyText: {
    fontSize: "14px",
    textAlign: "center",
    maxWidth: "400px",
    lineHeight: "1.5",
  },
  examples: {
    marginTop: "24px",
    display: "flex",
    flexDirection: "column",
    gap: "8px",
  },
  exampleLabel: {
    fontSize: "12px",
    color: "#666",
    textTransform: "uppercase",
    letterSpacing: "1px",
  },
  example: {
    fontSize: "13px",
    color: "#818cf8",
    padding: "8px 16px",
    backgroundColor: "#1e1e2e",
    borderRadius: "8px",
    border: "1px solid #333",
  },
  messageRow: {
    display: "flex",
  },
  bubble: {
    maxWidth: "min(80%, 600px)",
    padding: "12px 16px",
    borderRadius: "12px",
    fontSize: "14px",
    lineHeight: "1.6",
    wordBreak: "break-word",
    overflowWrap: "break-word",
  },
  userBubble: {
    backgroundColor: "#6366f1",
    color: "#fff",
    borderBottomRightRadius: "4px",
  },
  aiBubble: {
    backgroundColor: "#1e1e2e",
    color: "#e0e0e0",
    border: "1px solid #333",
    borderBottomLeftRadius: "4px",
  },
  aiText: {
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  loadingDots: {
    display: "flex",
    gap: "4px",
    padding: "4px 0",
  },
  dot: {
    fontSize: "24px",
    color: "#818cf8",
    animation: "pulse 1s infinite",
  },
};

export default ChatWindow;
