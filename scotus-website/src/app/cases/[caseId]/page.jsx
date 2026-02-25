import { getAllCaseIds, getCaseData } from "@/lib/cases";
import { CaseJsonLd } from "@/components/SEO/JsonLd";
import CaseStatusBadge from "@/components/CaseStatusBadge/CaseStatusBadge";
import CaseDetailClient from "./CaseDetailClient";
import styles from "./page.module.css";

export async function generateStaticParams() {
  const ids = getAllCaseIds();
  return ids.map((id) => ({ caseId: id }));
}

export async function generateMetadata({ params }) {
  const { caseId } = await params;
  const caseData = getCaseData(caseId);
  const topScenario = caseData.scenarios.reduce((a, b) =>
    a.probability > b.probability ? a : b
  );

  return {
    title: caseData.name,
    description: caseData.summary || caseData.questionPresented.slice(0, 155),
    openGraph: {
      title: `${caseData.name} — AI Prediction: ${topScenario.probability}% ${topScenario.shortLabel}`,
      description: caseData.questionPresented.slice(0, 200),
      type: "article",
      publishedTime: caseData.lastUpdated,
      siteName: "SCOTUS Predictor",
    },
    twitter: {
      card: "summary_large_image",
      title: `${caseData.name} — SCOTUS Predictor`,
      description: caseData.questionPresented.slice(0, 200),
    },
  };
}

export default async function CaseDetailPage({ params }) {
  const { caseId } = await params;
  const caseData = getCaseData(caseId);

  return (
    <article className={styles.page}>
      <CaseJsonLd caseData={caseData} />

      {/* Case header (server-rendered for SEO) */}
      <header className={styles.caseHeader}>
        <div className={styles.metaRow}>
          <CaseStatusBadge status={caseData.status} />
          <span className={styles.docket}>{caseData.docket}</span>
          <span className={styles.term}>{caseData.term}</span>
        </div>

        <h1 className={styles.caseName} style={{ fontFamily: "var(--font-serif)" }}>
          {caseData.name}
        </h1>

        <p className={styles.question}>{caseData.questionPresented}</p>

        <div className={styles.dates}>
          {caseData.argued && <span>Argued: {caseData.argued}</span>}
          {caseData.lowerCourt && <span>Lower court: {caseData.lowerCourt}</span>}
          <span>Last updated: {caseData.lastUpdated}</span>
        </div>
      </header>

      <hr />

      {/* Interactive content (client component) */}
      <CaseDetailClient caseData={caseData} />
    </article>
  );
}
