import React from "react";
import { JUSTICES_META, WING_COLORS, WING_LABELS } from "@/lib/constants";
import { italicizeCaseNames } from "@/lib/formatters";
import styles from "./JusticeVoteRow.module.css";

export default function JusticeVoteRow({ vote }) {
  const meta = JUSTICES_META[vote.name];
  const wingColor = WING_COLORS[meta?.wing] || "var(--color-text-muted)";
  const isAgainst = vote.prediction.toLowerCase().includes("against");

  return (
    <div className={styles.row}>
      <div className={styles.header}>
        <div className={styles.nameGroup}>
          <span className={styles.name}>{vote.name}</span>
          <span className={styles.wing} style={{ color: wingColor }}>
            {WING_LABELS[meta?.wing] || meta?.wing}
          </span>
        </div>
        <div className={styles.badges}>
          <span className={`${styles.prediction} ${isAgainst ? styles.against : styles.forGov}`}>
            {vote.prediction}
          </span>
          <span className={styles.confidence}>
            {vote.confidence} confidence
          </span>
        </div>
      </div>
      <div className={styles.reasoning}>
        {italicizeCaseNames(vote.reasoning, React)}
      </div>
    </div>
  );
}
