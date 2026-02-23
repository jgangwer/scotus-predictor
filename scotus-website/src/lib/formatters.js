import { SINGLE_CASE_NAMES } from "./constants";

/**
 * Takes a text string and returns an array of React elements
 * with Supreme Court case names automatically italicized.
 *
 * Uses two strategies:
 * 1. Regex matching "X v. Y" patterns (catches most case citations automatically)
 * 2. A supplementary list for single-name references (Chevron, Youngstown, etc.)
 */
export function italicizeCaseNames(text, React) {
  if (!text) return text;

  // Pattern for single-name case references from the supplementary list
  const singlePattern = SINGLE_CASE_NAMES
    .sort((a, b) => b.length - a.length)
    .map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");

  // Pattern for standard "X v. Y" case citations
  // Matches: "Humphrey's Executor v. United States", "Seila Law LLC v. CFPB", etc.
  const vCasePattern =
    "[A-Z][a-zA-Z'.\\u2019\\-]+(?:\\s+[A-Za-z'.\\u2019\\-]+)*\\s+v\\.\\s+[A-Z][a-zA-Z'.\\u2019\\-&,]+(?:\\s+[A-Za-z'.\\u2019\\-&,]+)*";

  // Combined: try "X v. Y" first (longer match), then single names
  const regex = new RegExp(`(${vCasePattern}|${singlePattern})`, "g");
  const parts = text.split(regex);

  return parts
    .map((part, i) => {
      if (!part) return null;
      // In split-with-capture-group, odd indices are the captured matches
      if (i % 2 === 1) {
        return React.createElement("em", { key: i }, part);
      }
      return part;
    })
    .filter(Boolean);
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
