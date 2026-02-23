import Link from "next/link";
import styles from "./Footer.module.css";

export default function Footer() {
  return (
    <footer className={styles.footer}>
      <div className={styles.inner}>
        <div className={styles.disclaimer}>
          <strong>Disclaimer:</strong> This is an AI-assisted prediction for educational
          and analytical purposes. It is not legal advice. Citations should be
          independently verified. Predictions reflect analytical modeling, not certainty.
        </div>
        <div className={styles.meta}>
          <span>Predictions generated using Claude (Anthropic)</span>
          <span className={styles.separator}>·</span>
          <Link href="/methodology">How this works</Link>
        </div>
      </div>
    </footer>
  );
}
