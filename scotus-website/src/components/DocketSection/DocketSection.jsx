"use client";

import { useState, useMemo } from "react";
import CaseCard from "@/components/CaseCard/CaseCard";
import CompactDocketRow from "@/components/CompactDocketRow/CompactDocketRow";
import DocketSearchBar from "@/components/DocketSearchBar/DocketSearchBar";
import styles from "./DocketSection.module.css";

const GROUP_ORDER = ["Argued", "Granted", "Decided"];

export default function DocketSection({ cases }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [collapsedGroups, setCollapsedGroups] = useState({});
  const [expandedCardId, setExpandedCardId] = useState(null);

  const filteredCases = useMemo(() => {
    if (!searchQuery.trim()) return cases;
    const q = searchQuery.toLowerCase();
    return cases.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.docket.toLowerCase().includes(q)
    );
  }, [cases, searchQuery]);

  const predictedCases = filteredCases.filter((c) => c.hasPrediction);
  const unpredictedCases = filteredCases.filter((c) => !c.hasPrediction);

  // Group unpredicted cases by status
  const groups = useMemo(() => {
    const grouped = {};
    for (const c of unpredictedCases) {
      const key = c.status;
      if (!grouped[key]) grouped[key] = [];
      grouped[key].push(c);
    }
    return GROUP_ORDER
      .filter((status) => grouped[status]?.length > 0)
      .map((status) => ({ status, cases: grouped[status] }));
  }, [unpredictedCases]);

  function toggleGroup(status) {
    setCollapsedGroups((prev) => ({ ...prev, [status]: !prev[status] }));
  }

  function toggleCard(id) {
    setExpandedCardId((prev) => (prev === id ? null : id));
  }

  // If only one group exists, don't show sub-group headers
  const showSubGroups = groups.length > 1;

  return (
    <div className={styles.section}>
      <DocketSearchBar
        value={searchQuery}
        onChange={setSearchQuery}
        resultCount={searchQuery ? filteredCases.length : null}
      />

      {/* Predicted cases — always full cards */}
      {predictedCases.length > 0 && (
        <div className={styles.predictedList}>
          {predictedCases.map((c) => (
            <CaseCard key={c.id} caseInfo={c} />
          ))}
        </div>
      )}

      {/* Unpredicted cases — grouped with collapsible headers */}
      {groups.map(({ status, cases: groupCases }) => (
        <div key={status} className={styles.subGroup}>
          {showSubGroups && (
            <div
              className={styles.subGroupHeader}
              onClick={() => toggleGroup(status)}
              role="button"
              tabIndex={0}
              aria-expanded={!collapsedGroups[status]}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  toggleGroup(status);
                }
              }}
            >
              <span
                className={`${styles.subGroupChevron} ${
                  collapsedGroups[status] ? styles.subGroupChevronCollapsed : ""
                }`}
              />
              <span className={styles.subGroupLabel}>{status}</span>
              <span className={styles.subGroupCount}>
                ({groupCases.length})
              </span>
            </div>
          )}

          {!collapsedGroups[status] && (
            <div className={styles.compactList}>
              {groupCases.map((c) => (
                <CompactDocketRow
                  key={c.id}
                  caseInfo={c}
                  isExpanded={expandedCardId === c.id}
                  onToggle={() => toggleCard(c.id)}
                />
              ))}
            </div>
          )}
        </div>
      ))}

      {filteredCases.length === 0 && searchQuery && (
        <div className={styles.noResults}>
          No cases match &ldquo;{searchQuery}&rdquo;
        </div>
      )}
    </div>
  );
}
