"use client";

import styles from "./ProbabilityChart.module.css";

const COLORS = ["#C4554D", "#4A7C8B", "#B8860B"];

export default function ProbabilityChart({ scenarios, onScenarioClick }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.label}>Outcome Probabilities</div>
      <div className={styles.bar}>
        {scenarios.map((s, i) => (
          <div
            key={s.id}
            className={styles.segment}
            style={{
              width: `${s.probability}%`,
              backgroundColor: COLORS[i % COLORS.length],
            }}
            onClick={() => onScenarioClick && onScenarioClick(s.id)}
            role="button"
            tabIndex={0}
            aria-label={`${s.shortLabel}: ${s.probability}%`}
          >
            <span className={styles.segmentLabel}>{s.probability}%</span>
          </div>
        ))}
      </div>
      <div className={styles.legend}>
        {scenarios.map((s, i) => (
          <div key={s.id} className={styles.legendItem}>
            <span
              className={styles.legendDot}
              style={{ backgroundColor: COLORS[i % COLORS.length] }}
            />
            <span className={styles.legendText}>
              {s.shortLabel} ({s.voteSplit})
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
