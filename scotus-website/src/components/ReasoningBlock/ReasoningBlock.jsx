import React from "react";
import { italicizeCaseNames } from "@/lib/formatters";
import styles from "./ReasoningBlock.module.css";

export default function ReasoningBlock({ label, summary, borderColor }) {
  return (
    <div
      className={styles.block}
      style={{ borderLeftColor: borderColor || "var(--color-border)" }}
    >
      <div className={styles.label}>{label}</div>
      <div className={styles.summary}>{italicizeCaseNames(summary, React)}</div>
    </div>
  );
}
