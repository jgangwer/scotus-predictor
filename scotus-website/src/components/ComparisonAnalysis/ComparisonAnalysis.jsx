"use client";

import styles from "./ComparisonAnalysis.module.css";

function ScoreBar({ name, score, maxScore, summary }) {
  const pct = (score / maxScore) * 100;
  const colorClass =
    score >= 7 ? styles.scoreHigh : score >= 5 ? styles.scoreMid : styles.scoreLow;

  return (
    <div className={styles.dimension}>
      <div className={styles.dimensionHeader}>
        <span className={styles.dimensionName}>{name}</span>
        <span className={`${styles.dimensionScore} ${colorClass}`}>
          {score}/{maxScore}
        </span>
      </div>
      <div className={styles.barTrack}>
        <div
          className={`${styles.barFill} ${colorClass}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className={styles.dimensionSummary}>{summary}</p>
    </div>
  );
}

export default function ComparisonAnalysis({ analysis }) {
  if (!analysis) return null;

  const avgScore =
    analysis.dimensions.reduce((sum, d) => sum + d.score, 0) /
    analysis.dimensions.length;

  return (
    <div className={styles.container}>
      {/* Overall grade */}
      <div className={styles.overallBox}>
        <div className={styles.gradeBadge}>
          <span className={styles.gradeLabel}>{analysis.overallLabel}</span>
          <span className={styles.gradeSubtext}>
            {analysis.overallScore}/10
          </span>
        </div>
        <p className={styles.overallSummary}>{analysis.summaryStatement}</p>
      </div>

      {/* Dimension scores */}
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Dimension Scores</h3>
        <div className={styles.dimensionList}>
          {analysis.dimensions.map((d) => (
            <ScoreBar
              key={d.name}
              name={d.name}
              score={d.score}
              maxScore={d.maxScore}
              summary={d.summary}
            />
          ))}
        </div>
      </section>

      {/* Key Hits */}
      <section className={styles.section}>
        <h3 className={`${styles.sectionTitle} ${styles.hitsTitle}`}>
          What We Got Right
        </h3>
        <ul className={styles.hitsList}>
          {analysis.keyHits.map((hit, i) => (
            <li key={i} className={styles.hitItem}>
              <span className={styles.hitIcon}>&#10003;</span>
              {hit}
            </li>
          ))}
        </ul>
      </section>

      {/* Key Misses */}
      <section className={styles.section}>
        <h3 className={`${styles.sectionTitle} ${styles.missesTitle}`}>
          What We Missed
        </h3>
        <ul className={styles.missesList}>
          {analysis.keyMisses.map((miss, i) => (
            <li key={i} className={styles.missItem}>
              <span className={styles.missIcon}>&#10007;</span>
              {miss}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
