import Link from "next/link";

export default function NotFound() {
  return (
    <div
      style={{
        maxWidth: "var(--max-width)",
        margin: "0 auto",
        padding: "6rem 1.5rem",
        textAlign: "center",
      }}
    >
      <h1
        style={{
          fontFamily: "var(--font-serif)",
          fontSize: "var(--text-3xl)",
          marginBottom: "1rem",
        }}
      >
        Page Not Found
      </h1>
      <p
        style={{
          color: "var(--color-text-secondary)",
          marginBottom: "2rem",
          fontSize: "var(--text-lg)",
        }}
      >
        The page you&rsquo;re looking for doesn&rsquo;t exist.
      </p>
      <Link
        href="/"
        style={{
          color: "var(--color-accent)",
          fontWeight: 600,
        }}
      >
        &larr; Back to docket
      </Link>
    </div>
  );
}
