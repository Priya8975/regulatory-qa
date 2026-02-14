/**
 * ConfidenceBadge — shows how reliable the answer is.
 *
 * The Compliance Checker agent returns a confidence score (0.0 to 1.0).
 * This component displays it as a colored badge:
 *   Green  (>= 0.8) — High confidence, all claims verified
 *   Yellow (0.6-0.8) — Moderate, some claims partially verified
 *   Red    (< 0.6)   — Low confidence, review sources carefully
 */

function ConfidenceBadge({ confidence, queryType }) {
  if (confidence === null || confidence === undefined) return null;

  const percentage = Math.round(confidence * 100);

  let color, label;
  if (confidence >= 0.8) {
    color = "#22c55e"; // green
    label = "High";
  } else if (confidence >= 0.6) {
    color = "#eab308"; // yellow
    label = "Moderate";
  } else {
    color = "#ef4444"; // red
    label = "Low";
  }

  return (
    <div style={styles.container}>
      <div style={{ ...styles.dot, backgroundColor: color }} />
      <div style={styles.info}>
        <span style={{ ...styles.label, color }}>{label} Confidence</span>
        <span style={styles.percentage}>{percentage}%</span>
      </div>
      {queryType && <span style={styles.queryType}>{queryType}</span>}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    padding: "8px 12px",
    backgroundColor: "#1e1e2e",
    borderRadius: "8px",
    border: "1px solid #333",
  },
  dot: {
    width: "10px",
    height: "10px",
    borderRadius: "50%",
    flexShrink: 0,
  },
  info: {
    display: "flex",
    flexDirection: "column",
    gap: "2px",
  },
  label: {
    fontSize: "12px",
    fontWeight: 600,
  },
  percentage: {
    fontSize: "11px",
    color: "#888",
  },
  queryType: {
    fontSize: "11px",
    color: "#666",
    marginLeft: "auto",
    padding: "2px 8px",
    backgroundColor: "#2a2a3e",
    borderRadius: "4px",
  },
};

export default ConfidenceBadge;
