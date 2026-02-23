import { CASE_NAMES } from "./constants";

/**
 * Takes a text string and returns an array of React elements
 * with Supreme Court case names automatically italicized.
 */
export function italicizeCaseNames(text, React) {
  if (!text) return text;
  const pattern = CASE_NAMES
    .sort((a, b) => b.length - a.length)
    .map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  const regex = new RegExp(`(${pattern})`, "g");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    CASE_NAMES.includes(part)
      ? React.createElement("em", { key: i }, part)
      : part
  );
}

/**
 * Format a date string for display.
 */
export function formatDate(dateStr) {
  if (!dateStr) return "";
  const date = new Date(dateStr + "T00:00:00");
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

/**
 * Slugify a case name for use in URLs.
 */
export function slugify(text) {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "");
}
