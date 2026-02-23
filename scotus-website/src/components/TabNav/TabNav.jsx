"use client";

import styles from "./TabNav.module.css";

export default function TabNav({ tabs, activeTab, onTabChange }) {
  return (
    <nav className={styles.tabs} role="tablist" aria-label="Case analysis views">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          className={`${styles.tab} ${activeTab === tab.id ? styles.active : ""}`}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
