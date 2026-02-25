"use client";

import CaseStatusBadge from "@/components/CaseStatusBadge/CaseStatusBadge";
import styles from "./CompactDocketRow.module.css";

export default function CompactDocketRow({ caseInfo, isExpanded, onToggle }) {
  const timelineLabel = getTimelineLabel(caseInfo);

  return (
    <div className={`${styles.wrapper} ${isExpanded ? styles.expanded : ""}`}>
      <div
        className={styles.row}
        onClick={onToggle}
        role="button"
        tabIndex={0}
        aria-expanded={isExpanded}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggle();
          }
        }}
      >
        <span className={styles.docket}>{caseInfo.docket}</span>
        <span className={styles.name}>{caseInfo.name}</span>
        <span className={`${styles.chevron} ${isExpanded ? styles.chevronOpen : ""}`} />
      </div>

      {isExpanded && (
        <div className={styles.detail}>
          <div className={styles.detailRow}>
            <CaseStatusBadge status={caseInfo.status} />
            {timelineLabel && (
              <span className={styles.timeline}>{timelineLabel}</span>
            )}
          </div>
          <div className={styles.noPrediction}>No prediction yet</div>
        </div>
      )}
    </div>
  );
}

function getTimelineLabel(caseInfo) {
  const tl = caseInfo.timeline;
  if (!tl) return null;
  if (tl.decided) return `Decided ${tl.decided}`;
  if (tl.argued) return `Argued ${tl.argued}`;
  if (tl.granted) return `Cert granted ${tl.granted}`;
  return null;
}
