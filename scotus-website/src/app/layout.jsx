import { Inter, Libre_Baskerville, JetBrains_Mono } from "next/font/google";
import { Analytics } from "@vercel/analytics/react";
import Header from "@/components/Header/Header";
import Footer from "@/components/Footer/Footer";
import "@/styles/globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const baskerville = Libre_Baskerville({
  weight: ["400", "700"],
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata = {
  title: {
    default: "SCOTUS Predictor — AI-Assisted Supreme Court Predictions",
    template: "%s — SCOTUS Predictor",
  },
  description:
    "AI-assisted predictions for pending Supreme Court cases, built from primary legal sources including briefs, oral argument transcripts, and voting data.",
  openGraph: {
    title: "SCOTUS Predictor",
    description:
      "AI-assisted predictions for pending Supreme Court cases, built from primary legal sources.",
    type: "website",
    siteName: "SCOTUS Predictor",
    url: "https://scotus-predictor.vercel.app",
  },
  twitter: {
    card: "summary_large_image",
    title: "SCOTUS Predictor",
    description:
      "AI-assisted predictions for pending Supreme Court cases, built from primary legal sources.",
  },
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${baskerville.variable} ${jetbrains.variable}`}
    >
      <body style={{ fontFamily: "var(--font-sans)" }}>
        <Header />
        <main>{children}</main>
        <Footer />
        <Analytics />
      </body>
    </html>
  );
}
