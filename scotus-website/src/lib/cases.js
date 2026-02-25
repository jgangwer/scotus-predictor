import fs from "fs";
import path from "path";

const CASES_DIR = path.join(process.cwd(), "src", "data", "cases");
const DATA_DIR = path.join(process.cwd(), "src", "data");

export function getAllCaseIds() {
  const index = JSON.parse(
    fs.readFileSync(path.join(CASES_DIR, "index.json"), "utf8")
  );
  return index.cases.map((c) => c.id);
}

export function getCaseData(caseId) {
  const filePath = path.join(CASES_DIR, `${caseId}.json`);
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

export function getAllCasesSummary() {
  const index = JSON.parse(
    fs.readFileSync(path.join(CASES_DIR, "index.json"), "utf8")
  );
  return index;
}

/**
 * Merges predicted cases from index.json with the full docket from docket_status.json.
 * Returns a unified list where predicted cases have full card data and
 * unpredicted cases have lightweight entries marked hasPrediction: false.
 */
export function getFullDocket() {
  const index = JSON.parse(
    fs.readFileSync(path.join(CASES_DIR, "index.json"), "utf8")
  );
  const docket = JSON.parse(
    fs.readFileSync(path.join(DATA_DIR, "docket_status.json"), "utf8")
  );

  // Build lookup: for each predicted case, track which raw docket numbers it covers
  const predictedCases = index.cases;
  const matchedDocketNumbers = new Set();

  const allCases = [];

  // Process each docket entry
  for (const [docketNum, entry] of Object.entries(docket.cases)) {
    // Check if this docket entry matches any predicted case
    const predicted = predictedCases.find((c) =>
      c.docket.includes(docketNum)
    );

    if (predicted) {
      // Avoid duplicates: if we already added this predicted case via another docket number
      if (!matchedDocketNumbers.has(predicted.id)) {
        matchedDocketNumbers.add(predicted.id);
        allCases.push({
          ...predicted,
          hasPrediction: true,
          timeline: entry.timeline,
        });
      }
    } else {
      // No prediction — create lightweight entry
      allCases.push({
        id: docketNum,
        name: entry.name.trim(),
        docket: `No. ${entry.docket}`,
        status: entry.decided
          ? "Decided"
          : entry.argued
            ? "Argued"
            : "Granted",
        hasPrediction: false,
        timeline: entry.timeline || {},
      });
    }
  }

  // Safety net: add any predicted cases that weren't found in docket_status
  for (const c of predictedCases) {
    if (!matchedDocketNumbers.has(c.id)) {
      allCases.push({ ...c, hasPrediction: true, timeline: {} });
    }
  }

  return {
    term: index.term,
    lastUpdated: index.lastUpdated,
    allCases,
    predictedCount: predictedCases.length,
    totalCount: allCases.length,
  };
}
