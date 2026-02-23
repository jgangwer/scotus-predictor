import Link from "next/link";
import styles from "./Header.module.css";

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.inner}>
        <Link href="/" className={styles.logo}>
          <span className={styles.logoMark} aria-hidden="true" />
          <span className={styles.logoText}>SCOTUS Predictor</span>
        </Link>
        <nav className={styles.nav} aria-label="Main navigation">
          <Link href="/" className={styles.navLink}>Docket</Link>
          <Link href="/methodology" className={styles.navLink}>Methodology</Link>
        </nav>
      </div>
      <div className={styles.tagline}>AI-Assisted Supreme Court Predictions</div>
    </header>
  );
}
