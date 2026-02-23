"use client";

import React from "react";
import { italicizeCaseNames } from "@/lib/formatters";
import { JUSTICES_META } from "@/lib/constants";
import ReasoningBlock from "@/components/ReasoningBlock/ReasoningBlock";
import styles from "./ScenarioCard.module.css";

const COLORS = ["#C4554D", "#4A7C8B", "#B8860B"];

function VoteDot({ justice, inMajority, accentColor }) {
  const meta = JUSTICES_META[justice];
  return (
    <div className={styles.voteDot} title={meta?.fullName || justice}>
      <div
        className={`${styles.dotCircle} ${inMajority ? styles.majority : styles.dissent}`}
        style={inMajority ? { borderColor: accentColor, color: accentColor } : {}}
      >
        {meta?.short || justice.slice(0, 2)}
      </div>
      <span className={`${styles.dotLabel} ${inMajority ? "" : styles.dissentLabel}`}>
        {inMajority ? "MAJ" : "DIS"}
      </span>
    </div>
  );
}

export default function ScenarioCard({ scenario, isExpanded, onToggle, id }) {
  const accentColor = COLORS[(scenario.id - 1) % COLORS.length];

  return (
    <article
      id={id}
      className={`${styles.card} ${isExpanded ? styles.expanded : ""}`}
      style={{ borderLeftColor: accentColor }}
    >
      {/* Header — always visible */}
      <div className={styles.header} onClick={onToggle} role="button" tabIndex={0}>
        <div className={styles.headerTop}>
          <div className={styles.headerLeft}>
            <span className={styles.scenarioLabel} style={{ color: accentColor }}>
              Scenario {scenario.id}
            </span>
            <h3 className={styles.title}>{scenario.title}</h3>
          </div>
          <div className={styles.headerRight}>
            <span className={styles.probability} style={{ color: accentColor }}>
              {scenario.probability}%
            </span>
            <span className={styles.probabilityLabel}>probability</span>
          </div>
        </div>

        <div className={styles.meta}>
          <span className={styles.voteSplit} style={{ borderColor: accentColor, color: accentColor }}>
            {scenario.voteSplit}
          </span>
          <span className={styles.authorLabel}>
            {scenario.author} writing for the majority
          </span>
        </div>

        {/* Vote dots */}
        <div className={styles.voteDots}>
          {[...scenario.majorityJustices, ...scenario.dissentJustices].map((j) => (
            <VoteDot
              key={j}
              justice={j}
              inMajority={scenario.majorityJustices.includes(j)}
              accentColor={accentColor}
            />
          ))}
        </div>

        <p className={styles.holding}>
          {italicizeCaseNames(scenario.holding, React)}
        </p>

        <div className={styles.expandLabel} style={{ color: accentColor }}>
          {isExpanded ? "▲ Collapse" : "▼ Expand full analysis"}
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div className={styles.body}>
          {/* Primary Reasoning */}
          <section>
            <div className={styles.sectionLabel} style={{ color: accentColor }}>
              Primary Legal Reasoning
            </div>
            <div className={styles.reasoningList}>
              {scenario.primaryReasoning.map((r, i) => (
                <ReasoningBlock
                  key={i}
                  label={r.label}
                  summary={r.summary}
                  borderColor={accentColor}
                />
              ))}
            </div>
          </section>

          {/* Concurrences */}
          {scenario.concurrences.length > 0 && (
            <section>
              <div className={styles.sectionLabel} style={{ color: "var(--color-scenario-3)" }}>
                Concurrences
              </div>
              {scenario.concurrences.map((c, i) => (
                <div key={i} className={styles.concurrenceBlock}>
                  <div className={styles.concurrenceAuthor}>
                    {c.author}
                    {c.joinedBy.length > 0
                      ? ` (joined by ${c.joinedBy.join(", ")})`
                      : " (concurring in judgment)"}
                  </div>
                  <div className={styles.concurrenceText}>
                    {italicizeCaseNames(c.summary, React)}
                  </div>
                </div>
              ))}
            </section>
          )}

          {/* Dissent */}
          <section>
            <div className={styles.sectionLabel} style={{ color: "var(--color-scenario-1)" }}>
              Dissent
            </div>
            <div className={styles.dissentBlock}>
              <div className={styles.dissentAuthor}>
                {scenario.dissent.author} (joined by {scenario.dissent.joinedBy.join(", ")})
              </div>
              <div className={styles.dissentArgs}>
                {scenario.dissent.coreArguments.map((arg, i) => (
                  <div key={i} className={styles.dissentArg}>
                    {italicizeCaseNames(arg, React)}
                  </div>
                ))}
              </div>
            </div>
          </section>

          {/* New Rule */}
          <section>
            <div className={styles.sectionLabel} style={{ color: "var(--color-confidence-very-high)" }}>
              What Changes Going Forward
            </div>
            <div className={styles.newRuleBlock}>
              {italicizeCaseNames(scenario.newRule, React)}
            </div>
          </section>
        </div>
      )}
    </article>
  );
}
