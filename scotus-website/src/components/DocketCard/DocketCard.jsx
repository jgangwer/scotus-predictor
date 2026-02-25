import CaseStatusBadge from "@/components/CaseStatusBadge/CaseStatusBadge";
import styles from "./DocketCard.module.css";

export default function DocketCard({ caseInfo }) {
  const timelineLabel = getTimelineLabel(caseInfo);

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <CaseStatusBadge status={caseInfo.status} />
        <span className={styles.docket}>{caseInfo.docket}</span>
      </div>
      <h3 className={styles.name}>{caseInfo.name}</h3>
      {timelineLabel && (
        <div className={styles.timeline}>{timelineLabel}</div>
      )}
      <div className={styles.noPrediction}>No prediction yet</div>
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
