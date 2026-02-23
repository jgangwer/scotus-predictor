"use client";

import { useState } from "react";
import TabNav from "@/components/TabNav/TabNav";
import ProbabilityChart from "@/components/ProbabilityChart/ProbabilityChart";
import ScenarioCard from "@/components/ScenarioCard/ScenarioCard";
import JusticeGrid from "@/components/JusticeGrid/JusticeGrid";
import styles from "./page.module.css";

const TABS = [
  { id: "scenarios", label: "Outcome Scenarios" },
  { id: "justices", label: "Justice-by-Justice" },
];

export default function CaseDetailClient({ caseData }) {
  const [activeTab, setActiveTab] = useState("scenarios");
  const [expandedScenario, setExpandedScenario] = useState(null);

  const handleScenarioClick = (id) => {
    setExpandedScenario(expandedScenario === id ? null : id);
    setTimeout(() => {
      const el = document.getElementById(`scenario-${id}`);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
    }, 100);
  };

  // Derive predicted outcome from justice votes
  const againstCount = caseData.justiceVotes.filter((v) =>
    v.prediction.toLowerCase().includes("against")
  ).length;
  const forCount = 9 - againstCount;
  const predictedOutcome = `${Math.max(againstCount, forCount)}\u2013${Math.min(againstCount, forCount)} ${againstCount > forCount ? "against" : "for"} the government. Thomas, Alito likely dissent. Kavanaugh is the swing \u2014 if he joins the majority, it\u2019s 7\u20132.`;

  return (
    <>
      <TabNav tabs={TABS} activeTab={activeTab} onTabChange={setActiveTab} />

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
          />
        </section>
      )}
    </>
  );
}
