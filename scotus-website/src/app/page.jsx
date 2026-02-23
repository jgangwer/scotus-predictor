import { getAllCasesSummary } from "@/lib/cases";
import { HomeJsonLd } from "@/components/SEO/JsonLd";
import CaseCard from "@/components/CaseCard/CaseCard";
import styles from "./page.module.css";

export default function HomePage() {
  const data = getAllCasesSummary();

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

      <section aria-label="Case predictions">
        <div className={styles.sectionLabel}>Pending Cases</div>
        <div className={styles.caseList}>
          {data.cases.map((c) => (
            <CaseCard key={c.id} caseInfo={c} />
          ))}
        </div>
      </section>
    </article>
  );
}
