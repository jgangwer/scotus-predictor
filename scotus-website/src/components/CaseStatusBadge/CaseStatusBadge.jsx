import styles from "./CaseStatusBadge.module.css";

export default function CaseStatusBadge({ status }) {
  const statusClass = status.toLowerCase().replace(/\s+/g, "-");
  return (
    <span className={`${styles.badge} ${styles[statusClass] || ""}`}>
      {status}
    </span>
  );
}
