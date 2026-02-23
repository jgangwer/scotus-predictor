import { getAllCasesSummary } from "@/lib/cases";
import { HomeJsonLd } from "@/components/SEO/JsonLd";
import CaseCard from "@/components/CaseCard/CaseCard";
import styles from "./page.module.css";

export default function HomePage() {
  const data = getAllCasesSummary();
  const decidedCases = data.cases.filter((c) => c.status === "Decided");
  const pendingCases = data.cases.filter((c) => c.status !== "Decided");

  return (
    <article className={styles.page}>
      <HomeJsonLd termData={data} />

      <header className={styles.header}>
        <h1 className={styles.title} style={{ fontFamily: "var(--font-serif)" }}>
          {data.term}
        </h1>
        <p className={styles.subtitle}>
          AI-generated predictions for {data.cases.length}{" "}
          {data.cases.length === 1 ? "case" : "cases"} before the Supreme Court,
          built from briefs, oral argument transcripts, and historical voting data.
        </p>
        <div className={styles.updated}>
          Last updated: {data.lastUpdated}
        </div>
      </header>

      <hr />

      {decidedCases.length > 0 && (
        <section aria-label="Decided cases">
          <div className={styles.sectionLabel}>Decided Cases</div>
          <div className={styles.caseList}>
            {decidedCases.map((c) => (
              <CaseCard key={c.id} caseInfo={c} />
            ))}
          </div>
        </section>
      )}

      {pendingCases.length > 0 && (
        <section aria-label="Pending cases">
          <div className={styles.sectionLabel}>Pending Cases</div>
          <div className={styles.caseList}>
            {pendingCases.map((c) => (
              <CaseCard key={c.id} caseInfo={c} />
            ))}
          </div>
        </section>
      )}
    </article>
  );
}
