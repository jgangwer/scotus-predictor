export function CaseJsonLd({ caseData }) {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: `${caseData.name} — Supreme Court Prediction`,
    description: caseData.questionPresented,
    datePublished: caseData.lastUpdated,
    dateModified: caseData.lastUpdated,
    author: {
      "@type": "Organization",
      name: "SCOTUS Predictor",
    },
    publisher: {
      "@type": "Organization",
      name: "SCOTUS Predictor",
    },
    mainEntity: {
      "@type": "LegalCase",
      name: caseData.name,
      identifier: caseData.docket,
      court: {
        "@type": "GovernmentOrganization",
        name: "Supreme Court of the United States",
      },
    },
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}

export function HomeJsonLd({ termData }) {
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "SCOTUS Predictor",
    description: "AI-assisted predictions for pending Supreme Court cases, built from primary legal sources.",
    url: "https://scotus-predictor.vercel.app",
  };

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
    />
  );
}
