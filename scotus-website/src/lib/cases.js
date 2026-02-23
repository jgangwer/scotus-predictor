import fs from "fs";
import path from "path";

const CASES_DIR = path.join(process.cwd(), "src", "data", "cases");

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
