export const JUSTICES_META = {
  Roberts: { wing: "center-right", short: "JR", fullName: "Chief Justice Roberts" },
  Thomas: { wing: "conservative", short: "CT", fullName: "Justice Thomas" },
  Alito: { wing: "conservative", short: "SA", fullName: "Justice Alito" },
  Sotomayor: { wing: "liberal", short: "SS", fullName: "Justice Sotomayor" },
  Kagan: { wing: "liberal", short: "EK", fullName: "Justice Kagan" },
  Gorsuch: { wing: "conservative", short: "NG", fullName: "Justice Gorsuch" },
  Kavanaugh: { wing: "center-right", short: "BK", fullName: "Justice Kavanaugh" },
  Barrett: { wing: "conservative", short: "ACB", fullName: "Justice Barrett" },
  Jackson: { wing: "liberal", short: "KBJ", fullName: "Justice Jackson" },
};

export const WING_COLORS = {
  "liberal": "var(--color-wing-liberal)",
  "center-right": "var(--color-wing-center)",
  "conservative": "var(--color-wing-conservative)",
};

export const WING_LABELS = {
  "liberal": "Liberal",
  "center-right": "Center-Right",
  "conservative": "Conservative",
};

export const CONFIDENCE_COLORS = {
  "Very High": "var(--color-confidence-very-high)",
  "High": "var(--color-confidence-high)",
  "Moderate-High": "var(--color-confidence-moderate)",
  "Moderate": "var(--color-confidence-moderate)",
  "Low": "var(--color-confidence-low)",
};

export const SCENARIO_COLORS = [
  "var(--color-scenario-1)",
  "var(--color-scenario-2)",
  "var(--color-scenario-3)",
];

// Single-name case references that can't be caught by the "X v. Y" regex pattern.
// The regex in formatters.js auto-catches all "X v. Y" citations.
export const SINGLE_CASE_NAMES = [
  "Humphrey\u2019s Executor",
  "Humphrey's Executor",
  "Loper Bright",
  "Seila Law",
  "Curtiss-Wright",
  "Dames & Moore",
  "Brown & Williamson",
  "Chevron",
  "Youngstown",
  "Algonquin",
  "Gundy",
  "Whitman",
  "Morrison",
  "Collins",
];
