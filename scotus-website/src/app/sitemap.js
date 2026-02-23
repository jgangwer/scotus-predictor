import { getAllCaseIds } from "@/lib/cases";

export default function sitemap() {
  const caseIds = getAllCaseIds();
  const baseUrl = "https://scotus-predictor.vercel.app";

  const casePages = caseIds.map((id) => ({
    url: `${baseUrl}/cases/${id}`,
    lastModified: new Date(),
    changeFrequency: "weekly",
    priority: 0.8,
  }));

  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1.0,
    },
    {
      url: `${baseUrl}/methodology`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.5,
    },
    ...casePages,
  ];
}
