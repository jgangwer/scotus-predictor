"use client";

import styles from "./DocketSearchBar.module.css";

export default function DocketSearchBar({ value, onChange, placeholder, resultCount }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.inputRow}>
        <input
          type="search"
          className={styles.input}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || "Filter by case name or docket number\u2026"}
          aria-label="Filter cases"
        />
        {value && (
          <button
            className={styles.clear}
            onClick={() => onChange("")}
            aria-label="Clear search"
            type="button"
          >
            &times;
          </button>
        )}
      </div>
      {value && resultCount != null && (
        <div className={styles.resultCount}>
          {resultCount} {resultCount === 1 ? "case" : "cases"} found
        </div>
      )}
    </div>
  );
}
