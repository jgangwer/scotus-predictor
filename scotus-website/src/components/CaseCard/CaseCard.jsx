import Link from "next/link";
import CaseStatusBadge from "@/components/CaseStatusBadge/CaseStatusBadge";
import styles from "./CaseCard.module.css";

const COLORS = ["#C4554D", "#4A7C8B", "#B8860B"];

export default function CaseCard({ caseInfo }) {
  const scenarios = caseInfo.scenarios;

  return (
    <Link href={`/cases/${caseInfo.id}`} className={styles.card}>
      <div className={styles.header}>
        <CaseStatusBadge status={caseInfo.status} />
        <span className={styles.docket}>{caseInfo.docket}</span>
      </div>
      <h2 className={styles.name}>{caseInfo.name}</h2>
      <p className={styles.summary}>{caseInfo.summary}</p>

      {scenarios && scenarios.length > 0 && (
        <div className={styles.chartWrapper}>
          <div className={styles.chartLabel}>Outcome Probabilities</div>
          <div className={styles.chartBar}>
            {scenarios.map((s, i) => (
              <div
                key={s.id}
                className={styles.chartSegment}
                style={{
                  width: `${s.probability}%`,
                  backgroundColor: COLORS[i % COLORS.length],
                }}
                aria-label={`${s.shortLabel}: ${s.probability}%`}
              >
                <span className={styles.chartSegmentLabel}>
                  {s.probability}%
                </span>
              </div>
            ))}
          </div>
          <div className={styles.chartLegend}>
            {scenarios.map((s, i) => (
              <div key={s.id} className={styles.chartLegendItem}>
                <span
                  className={styles.chartLegendDot}
                  style={{ backgroundColor: COLORS[i % COLORS.length] }}
                />
                <span className={styles.chartLegendText}>
                  {s.shortLabel} ({s.voteSplit})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className={styles.tags}>
        {caseInfo.tags?.map((tag) => (
          <span key={tag} className={styles.tag}>{tag}</span>
        ))}
      </div>
    </Link>
  );
}
