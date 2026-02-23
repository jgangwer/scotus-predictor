export default function robots() {
  return {
    rules: [
      {
        userAgent: "*",
        allow: "/",
      },
    ],
    sitemap: "https://scotus-predictor.vercel.app/sitemap.xml",
  };
}
