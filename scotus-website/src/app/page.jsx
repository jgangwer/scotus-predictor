import { getFullDocket } from "@/lib/cases";
import { HomeJsonLd } from "@/components/SEO/JsonLd";
import CaseCard from "@/components/CaseCard/CaseCard";
import DocketCard from "@/components/DocketCard/DocketCard";
import styles from "./page.module.css";

/**
 * Sort cases: predicted first, then unpredicted sorted by pipeline stage
 * (argued before granted) and by most recent date.
 */
function sortCases(cases) {
  return [...cases].sort((a, b) => {
    // Predicted cases always come first
    if (a.hasPrediction && !b.hasPrediction) return -1;
    if (!a.hasPrediction && b.hasPrediction) return 1;

    // Among unpredicted: argued > granted (closer to decision first)
    if (!a.hasPrediction && !b.hasPrediction) {
      const stageOrder = { Argued: 0, Granted: 1, Decided: 2 };
      const aStage = stageOrder[a.status] ?? 99;
      const bStage = stageOrder[b.status] ?? 99;
      if (aStage !== bStage) return aStage - bStage;
    }

    return 0;
  });
}

export default function HomePage() {
  const data = getFullDocket();
  const pendingCases = sortCases(
    data.allCases.filter((c) => c.status !== "Decided")
  );
  const decidedCases = sortCases(
    data.allCases.filter((c) => c.status === "Decided")
  );

  return (
    <article className={styles.page}>
      <HomeJsonLd termData={data} />

      <header className={styles.header}>
        <h1 className={styles.title} style={{ fontFamily: "var(--font-serif)" }}>
          {data.term}
        </h1>
        <p className={styles.subtitle}>
          AI-generated predictions for {data.predictedCount} of{" "}
          {data.totalCount} cases before the Supreme Court,
          built from briefs, oral argument transcripts, and historical voting data.
        </p>
        <div className={styles.updated}>
          Last updated: {data.lastUpdated}
        </div>
      </header>

      <hr />

      {pendingCases.length > 0 && (
        <section aria-label="Pending cases">
          <div className={styles.sectionLabel}>Pending Cases</div>
          <div className={styles.caseList}>
            {pendingCases.map((c) =>
              c.hasPrediction ? (
                <CaseCard key={c.id} caseInfo={c} />
              ) : (
                <DocketCard key={c.id} caseInfo={c} />
              )
            )}
          </div>
        </section>
      )}

      {decidedCases.length > 0 && (
        <section aria-label="Decided cases">
          <div className={styles.sectionLabel}>Decided Cases</div>
          <div className={styles.caseList}>
            {decidedCases.map((c) =>
              c.hasPrediction ? (
                <CaseCard key={c.id} caseInfo={c} />
              ) : (
                <DocketCard key={c.id} caseInfo={c} />
              )
            )}
          </div>
        </section>
      )}
    </article>
  );
}
