import Link from "next/link";
import CaseStatusBadge from "@/components/CaseStatusBadge/CaseStatusBadge";
import styles from "./CaseCard.module.css";

export default function CaseCard({ caseInfo }) {
  return (
    <Link href={`/cases/${caseInfo.id}`} className={styles.card}>
      <div className={styles.header}>
        <CaseStatusBadge status={caseInfo.status} />
        <span className={styles.docket}>{caseInfo.docket}</span>
      </div>
      <h2 className={styles.name}>{caseInfo.name}</h2>
      <p className={styles.summary}>{caseInfo.summary}</p>
      <div className={styles.footer}>
        <div className={styles.prediction}>
          <span className={styles.predictionProb}>
            {caseInfo.topPrediction?.probability}%
          </span>
          <span className={styles.predictionLabel}>
            {caseInfo.topPrediction?.outcome}
          </span>
        </div>
        <span className={styles.outcome}>{caseInfo.topPrediction?.voteSplit}</span>
      </div>
      <div className={styles.tags}>
        {caseInfo.tags?.map((tag) => (
          <span key={tag} className={styles.tag}>{tag}</span>
        ))}
      </div>
    </Link>
  );
}
