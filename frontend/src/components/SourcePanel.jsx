/**
 * SourcePanel — displays the source documents used to generate the answer.
 *
 * This is the right sidebar. For each answer, it shows:
 * - Which regulation the source came from
 * - The page number
 * - A snippet of the actual text
 *
 * This lets users verify the AI's answer against the original sources.
 * In regulated industries, this traceability is essential.
 */

function SourcePanel({ sources }) {
  if (!sources || sources.length === 0) {
    return (
      <div style={styles.container}>
        <h3 style={styles.title}>Sources</h3>
        <p style={styles.emptyText}>
          Sources will appear here when you ask a question.
          Each answer is grounded in specific regulatory passages.
        </p>
      </div>
    );
  }

  // Group sources by regulation for cleaner display
  const grouped = {};
  sources.forEach((source) => {
    const reg = source.regulation;
    if (!grouped[reg]) grouped[reg] = [];
    grouped[reg].push(source);
  });

  return (
    <div style={styles.container}>
      <h3 style={styles.title}>Sources ({sources.length})</h3>

      {Object.entries(grouped).map(([regulation, docs]) => (
        <div key={regulation} style={styles.group}>
          <h4 style={styles.groupTitle}>{regulation}</h4>

          {docs.map((doc, index) => (
            <div key={index} style={styles.card}>
              <div style={styles.cardHeader}>
                <span style={styles.page}>Page {doc.page + 1}</span>
              </div>
              <p style={styles.content}>{doc.content}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

const styles = {
  container: {
    height: "100%",
    overflowY: "auto",
    padding: "16px",
    backgroundColor: "#12121e",
  },
  title: {
    fontSize: "16px",
    fontWeight: 600,
    color: "#e0e0e0",
    marginBottom: "16px",
    paddingBottom: "8px",
    borderBottom: "1px solid #333",
  },
  emptyText: {
    fontSize: "13px",
    color: "#666",
    lineHeight: "1.6",
  },
  group: {
    marginBottom: "16px",
  },
  groupTitle: {
    fontSize: "13px",
    fontWeight: 600,
    color: "#818cf8",
    marginBottom: "8px",
    textTransform: "uppercase",
    letterSpacing: "0.5px",
  },
  card: {
    padding: "10px 12px",
    backgroundColor: "#1e1e2e",
    borderRadius: "8px",
    border: "1px solid #2a2a3e",
    marginBottom: "8px",
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    marginBottom: "6px",
  },
  page: {
    fontSize: "11px",
    color: "#888",
    fontWeight: 500,
  },
  content: {
    fontSize: "12px",
    color: "#aaa",
    lineHeight: "1.5",
    margin: 0,
    // Limit the displayed text to 4 lines
    display: "-webkit-box",
    WebkitLineClamp: 4,
    WebkitBoxOrient: "vertical",
    overflow: "hidden",
  },
};

export default SourcePanel;
