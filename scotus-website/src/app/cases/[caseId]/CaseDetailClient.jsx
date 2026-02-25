"use client";

import { useState } from "react";
import TabNav from "@/components/TabNav/TabNav";
import ProbabilityChart from "@/components/ProbabilityChart/ProbabilityChart";
import ScenarioCard from "@/components/ScenarioCard/ScenarioCard";
import JusticeGrid from "@/components/JusticeGrid/JusticeGrid";
import ComparisonAnalysis from "@/components/ComparisonAnalysis/ComparisonAnalysis";
import styles from "./page.module.css";

export default function CaseDetailClient({ caseData }) {
  const [activeTab, setActiveTab] = useState("scenarios");
  const [expandedScenario, setExpandedScenario] = useState(null);

  // Build tabs dynamically — add "Prediction Accuracy" only for decided cases
  const tabs = [
    { id: "scenarios", label: "Outcome Scenarios" },
    { id: "justices", label: "Justice-by-Justice" },
    ...(caseData.comparisonAnalysis
      ? [{ id: "comparison", label: "Prediction Accuracy" }]
      : []),
  ];

  const handleScenarioClick = (id) => {
    setExpandedScenario(expandedScenario === id ? null : id);
    setTimeout(() => {
      const el = document.getElementById(`scenario-${id}`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  };

  // Derive predicted outcome from justice votes using case-specific sides
  const sides = caseData.predictionSides || {
    sideA: { label: "Side A", matchTerms: [] },
    sideB: { label: "Side B", matchTerms: [] },
  };
  const sideACount = caseData.justiceVotes.filter((v) =>
    sides.sideA.matchTerms.some((t) => v.prediction.toLowerCase().includes(t))
  ).length;
  const sideBCount = 9 - sideACount;
  const majorityLabel = sideACount > sideBCount ? sides.sideA.label : sides.sideB.label;
  const majorityCount = Math.max(sideACount, sideBCount);
  const minorityCount = Math.min(sideACount, sideBCount);
  const predictedOutcome = `${majorityCount}\u2013${minorityCount}: ${majorityLabel}`;

  // Determine which scenario the opinion PDFs belong to
  const opinionScenarioId = caseData.opinionScenario || 1;
  const opinionPDFs = caseData.opinionPDFs || [];

  return (
    <>
      <TabNav tabs={tabs} activeTab={activeTab} onTabChange={setActiveTab} />

      {activeTab === "scenarios" && (
        <section role="tabpanel" aria-label="Outcome scenarios">
          <ProbabilityChart
            scenarios={caseData.scenarios}
            onScenarioClick={handleScenarioClick}
          />

          <div className={styles.scenarioList}>
            {caseData.scenarios.map((s) => (
              <ScenarioCard
                key={s.id}
                scenario={s}
                isExpanded={expandedScenario === s.id}
                onToggle={() => handleScenarioClick(s.id)}
                id={`scenario-${s.id}`}
                opinionPDFs={s.id === opinionScenarioId ? opinionPDFs : undefined}
                caseId={caseData.id}
              />
            ))}
          </div>
        </section>
      )}

      {activeTab === "justices" && (
        <section role="tabpanel" aria-label="Justice-by-justice predictions">
          <JusticeGrid
            justiceVotes={caseData.justiceVotes}
            predictedOutcome={predictedOutcome}
            predictionSides={sides}
          />
        </section>
      )}

      {activeTab === "comparison" && caseData.comparisonAnalysis && (
        <section role="tabpanel" aria-label="Prediction accuracy analysis">
          <ComparisonAnalysis analysis={caseData.comparisonAnalysis} />
        </section>
      )}
    </>
  );
}
