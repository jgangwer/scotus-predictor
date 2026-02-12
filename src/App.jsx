import { useState } from "react";

const CASES = [
  {
    id: "learning-resources-v-trump",
    name: "Learning Resources v. Trump",
    docket: "Nos. 24-1287 & 25-250",
    term: "October Term 2025",
    argued: "November 5, 2025",
    status: "Awaiting Decision",
    questionPresented: "Whether the International Emergency Economic Powers Act (IEEPA) authorizes the President to impose sweeping tariffs on imports, and if so, whether such delegation is constitutional.",
    lastUpdated: "2026-02-12",
    scenarios: [
      {
        id: 1,
        title: "THE MAJOR QUESTIONS BLOCKADE",
        shortLabel: "Major Questions",
        probability: 55,
        voteSplit: "6–3",
        holding: "IEEPA does not authorize tariffs of this magnitude. \"Regulate importation\" does not clearly grant tariff-imposing authority. Under the major questions doctrine, decisions of vast economic and political significance require clear congressional authorization.",
        author: "Roberts",
        majorityJustices: ["Roberts", "Sotomayor", "Kagan", "Gorsuch", "Barrett", "Jackson"],
        dissentJustices: ["Thomas", "Alito", "Kavanaugh"],
        primaryReasoning: [
          {
            label: "Textual Analysis",
            summary: "\"Regulate\" sits alongside blocking/sanctioning verbs — it means control entry, not impose duties. Congress used explicit tariff language in §232, §301, and §122 but not in IEEPA. Expressio unius: when Congress intended tariffs, it said so."
          },
          {
            label: "Structural Coherence",
            summary: "Reading IEEPA to authorize unlimited tariffs renders Trade Act §122 superfluous. Congress enacted §122 (15% cap, 150-day limit) just three years before IEEPA — it wouldn't have bothered if IEEPA already provided uncapped authority."
          },
          {
            label: "Major Questions Doctrine",
            summary: "Even if ambiguous, these tariffs generate $5.2T over 10 years — dwarfing the actions struck down in West Virginia v. EPA and Biden v. Nebraska. No President invoked IEEPA for tariffs in 48 years of existence."
          },
          {
            label: "Constitutional Avoidance",
            summary: "Reading IEEPA to authorize open-ended tariff authority raises nondelegation concerns. The government conceded that if 48-year trade deficits qualify as \"unusual,\" virtually any economic dissatisfaction would suffice."
          }
        ],
        concurrences: [
          {
            author: "Gorsuch",
            joinedBy: ["Thomas"],
            summary: "The major questions doctrine is grounded in nondelegation. Delegating unlimited tariff-setting authority with no intelligible principle beyond \"unusual and extraordinary threat\" violates Article I. The Founders separately enumerated \"Duties\" and \"Imposts\" to ensure congressional control."
          },
          {
            author: "Barrett",
            joinedBy: [],
            summary: "Foreign affairs deference does not override Congress's explicit occupation of the field. Tariffs are domestic economic policy with foreign effects, not pure diplomatic relations. Youngstown Category 3 applies."
          }
        ],
        dissent: {
          author: "Thomas",
          joinedBy: ["Alito", "Kavanaugh"],
          coreArguments: [
            "\"Regulate\" plainly includes tariffs — they control terms of entry. If IEEPA authorizes prohibition (which the majority concedes), it must authorize the lesser step of conditioning entry on duties.",
            "§122 is not surplusage — it covers different emergencies (balance-of-payments) with streamlined procedures. Multiple authorities coexist throughout the U.S. Code.",
            "Algonquin controls: §232's \"adjust imports\" authorized license fees (functionally equivalent to tariffs). IEEPA uses parallel language.",
            "Major questions doctrine developed for agencies, not the President acting in foreign affairs/national security based on express statutory delegation.",
            "Courts lack competence to second-guess presidential judgments about what constitutes a foreign threat. Curtiss-Wright, Dames & Moore establish deference."
          ]
        },
        newRule: "Tariff authority — explicitly vested in Congress by Article I — requires express congressional authorization. Presidents must use Trade Act mechanisms (§122, §232, §301) with their procedural requirements and substantive limits. IEEPA retains authority for asset freezes, transaction prohibitions, and import blocking in genuine foreign emergencies."
      },
      {
        id: 2,
        title: "THE NONDELEGATION REVIVAL",
        shortLabel: "Nondelegation",
        probability: 25,
        voteSplit: "5–4",
        holding: "IEEPA's delegation of tariff authority, if the statute provides it, violates the nondelegation doctrine. Congress may not delegate its Article I tariff power without an intelligible principle that meaningfully constrains executive discretion.",
        author: "Gorsuch",
        majorityJustices: ["Gorsuch", "Roberts", "Thomas", "Alito", "Barrett"],
        dissentJustices: ["Sotomayor", "Kagan", "Kavanaugh", "Jackson"],
        primaryReasoning: [
          {
            label: "Nondelegation Framework",
            summary: "Article I vests ALL legislative powers in Congress. IEEPA provides no guidance on rates, duration, countries, or products — \"unusual and extraordinary threat\" could mean anything. The government conceded 48-year trade deficits qualify."
          },
          {
            label: "Article I, §8 Specificity",
            summary: "The Founders separately enumerated \"Duties\" and \"Imposts\" to ensure congressional control. Tariffs are taxes on Americans — the Founders rejected taxation without representation precisely because taxes require popular accountability."
          },
          {
            label: "Distinguished Precedent",
            summary: "Prior upheld tariff authorities (§232, §122, §301) all provide real standards — specific triggers, caps, time limits, procedural requirements. IEEPA provides none."
          }
        ],
        concurrences: [
          {
            author: "Thomas",
            joinedBy: [],
            summary: "Even the majority's framework is too permissive. Legislative power — creating binding rules of general applicability — cannot be delegated at all, regardless of intelligible principles."
          }
        ],
        dissent: {
          author: "Kagan",
          joinedBy: ["Sotomayor", "Kavanaugh", "Jackson"],
          coreArguments: [
            "The intelligible principle test has worked for nearly a century. The majority's new tiered framework has no basis in text or precedent.",
            "Congress has repeatedly reauthorized IEEPA knowing how broadly it has been used. Acquiescence demonstrates legislative acceptance.",
            "The practical consequences are staggering — dozens of existing delegations become suspect overnight.",
            "The majority conflates policy disagreement with constitutional violation. If IEEPA's standards are insufficient, Congress can amend the statute."
          ]
        },
        newRule: "New tiered nondelegation framework. Tier 1 (core legislative functions like taxation): intelligible principle must be meaningfully constraining with specific triggers, bounded remedies, and procedural safeguards. Tier 2 (executive/administrative): traditional rational basis review. Article I, §8 powers get enhanced protection."
      },
      {
        id: 3,
        title: "GOVERNMENT PREVAILS",
        shortLabel: "Gov. Prevails",
        probability: 20,
        voteSplit: "5–4",
        holding: "IEEPA's authorization to \"regulate importation\" encompasses tariffs. The President's determination of a national emergency is entitled to substantial deference in matters of foreign affairs, and the major questions doctrine does not apply to presidential action in this domain.",
        author: "Kavanaugh",
        majorityJustices: ["Kavanaugh", "Roberts", "Thomas", "Alito", "Barrett"],
        dissentJustices: ["Sotomayor", "Kagan", "Gorsuch", "Jackson"],
        primaryReasoning: [
          {
            label: "Plain Text",
            summary: "\"Regulate\" plainly encompasses tariffs — conditioning importation on payment of duties is a classic form of import regulation. If the President can prohibit imports entirely, he can impose the lesser restriction of tariffs."
          },
          {
            label: "Foreign Affairs Deference",
            summary: "Curtiss-Wright, Dames & Moore, and Haig v. Agee establish broad presidential authority in foreign affairs. Trade policy is inherently a foreign affairs function, and courts lack competence to second-guess emergency determinations."
          },
          {
            label: "Major Questions Inapplicable",
            summary: "The doctrine addresses agency assertions of novel authority, not presidential action in areas of inherent Article II power based on express statutory delegation that Congress has repeatedly reauthorized."
          }
        ],
        concurrences: [],
        dissent: {
          author: "Gorsuch",
          joinedBy: ["Sotomayor", "Kagan", "Jackson"],
          coreArguments: [
            "The Constitution explicitly vests tariff authority in Congress. The majority's \"foreign affairs\" characterization ignores that tariffs are taxes on Americans.",
            "48 years of non-use demonstrates that no prior administration believed IEEPA authorized tariffs.",
            "The majority's reading renders §122, §232, and §301 — with their careful limits — superfluous.",
            "If \"regulate importation\" includes unlimited tariffs, then IEEPA grants the President a blank check over the entire U.S. economy, subject only to his own emergency declaration."
          ]
        },
        newRule: "IEEPA authorizes tariffs as a form of import regulation. Presidential emergency determinations in foreign affairs receive substantial deference. Major questions doctrine does not apply to presidential actions under express statutory delegation in the foreign affairs domain."
      }
    ],
    justiceVotes: [
      { name: "Roberts", prediction: "Against tariffs", confidence: "High", reasoning: "Referred to tariffs as a \"core\" congressional power. His institutional instinct favors narrow statutory interpretation over constitutional confrontation. Likely writes majority opinion on statutory grounds." },
      { name: "Thomas", prediction: "For tariffs", confidence: "Moderate", reasoning: "Broad textualist reading of \"regulate.\" Strong deference to executive in foreign affairs. But nondelegation concerns could pull him — he's written extensively about limiting congressional delegation." },
      { name: "Alito", prediction: "For tariffs", confidence: "High", reasoning: "Most sympathetic to administration at oral argument. Observed that emergency powers statutes are often phrased broadly. Consistent deference to executive authority in national security." },
      { name: "Sotomayor", prediction: "Against tariffs", confidence: "Very High", reasoning: "Called the administration's position a \"blank check.\" Emphasized absence of tariff-specific language in IEEPA. Strongest voice for challengers at oral argument." },
      { name: "Kagan", prediction: "Against tariffs", confidence: "Very High", reasoning: "Pressed hard on surplusage — why would Congress enact §122's careful limits if IEEPA already provided unlimited authority? Skeptical of government's statutory reading throughout." },
      { name: "Gorsuch", prediction: "Against tariffs", confidence: "High", reasoning: "Nondelegation hawk. IEEPA's lack of constraining standards is exactly what he's warned about since Gundy. May concur on nondelegation grounds rather than joining a pure statutory interpretation majority." },
      { name: "Kavanaugh", prediction: "Lean against tariffs", confidence: "Moderate", reasoning: "The true swing vote. Extensive questioning at oral argument suggests working through the problem, not committed to either side. Foreign affairs deference instincts compete with statutory text concerns." },
      { name: "Barrett", prediction: "Against tariffs", confidence: "Moderate-High", reasoning: "Emphasized absence of \"tariffs,\" \"duties,\" or \"taxes\" in IEEPA. Distinguished domestic economic policy from foreign affairs. But could be swayed by institutional concerns about disrupting trade negotiations." },
      { name: "Jackson", prediction: "Against tariffs", confidence: "Very High", reasoning: "Aligned with Sotomayor and Kagan throughout oral argument. Focused on congressional power under Article I and the comprehensive statutory scheme Congress built for tariff delegation." }
    ]
  }
];

const JUSTICES_META = {
  Roberts: { wing: "center-right", short: "JR" },
  Thomas: { wing: "conservative", short: "CT" },
  Alito: { wing: "conservative", short: "SA" },
  Sotomayor: { wing: "liberal", short: "SS" },
  Kagan: { wing: "liberal", short: "EK" },
  Gorsuch: { wing: "conservative", short: "NG" },
  Kavanaugh: { wing: "center-right", short: "BK" },
  Barrett: { wing: "conservative", short: "ACB" },
  Jackson: { wing: "liberal", short: "KBJ" },
};

const WING_COLORS = {
  "liberal": "#60a5fa",
  "center-right": "#a78bfa",
  "conservative": "#f87171",
};

const CONFIDENCE_COLORS = {
  "Very High": "#4ade80",
  "High": "#a3e635",
  "Moderate-High": "#facc15",
  "Moderate": "#fb923c",
  "Lean against tariffs": "#fb923c",
};

const CASE_NAMES = [
  "West Virginia v. EPA",
  "Biden v. Nebraska",
  "Youngstown",
  "Algonquin",
  "Curtiss-Wright",
  "Dames & Moore",
  "Haig v. Agee",
  "Gundy",
  "Loper Bright",
  "Chevron",
  "Marbury v. Madison",
  "Field v. Clark",
  "Whitman",
  "Brown & Williamson",
];

function italicizeCaseNames(text) {
  if (!text) return text;
  const pattern = CASE_NAMES
    .sort((a, b) => b.length - a.length)
    .map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .join('|');
  const regex = new RegExp(`(${pattern})`, 'g');
  const parts = text.split(regex);
  return parts.map((part, i) =>
    CASE_NAMES.includes(part)
      ? <em key={i} style={{ fontStyle: "italic" }}>{part}</em>
      : part
  );
}

function ProbabilityBar({ probability, accent }) {
  return (
    <div style={{
      width: "100%",
      height: 6,
      background: "#ffffff08",
      borderRadius: 3,
      overflow: "hidden",
      marginTop: 8,
    }}>
      <div style={{
        width: `${probability}%`,
        height: "100%",
        background: accent,
        borderRadius: 3,
        transition: "width 0.8s ease",
      }} />
    </div>
  );
}

function VoteDot({ justice, inMajority, accent }) {
  const meta = JUSTICES_META[justice];
  const color = inMajority ? accent : "#ffffff22";
  return (
    <div style={{
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      gap: 4,
    }} title={justice}>
      <div style={{
        width: 32,
        height: 32,
        borderRadius: "50%",
        background: inMajority ? color + "22" : "#ffffff06",
        border: `2px solid ${color}`,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 10,
        fontWeight: 700,
        color: inMajority ? color : "#555",
        letterSpacing: "0.02em",
      }}>
        {meta.short}
      </div>
      <span style={{
        fontSize: 9,
        color: inMajority ? "#9ca3af" : "#444",
        letterSpacing: "0.05em",
      }}>
        {inMajority ? "MAJ" : "DIS"}
      </span>
    </div>
  );
}

function ScenarioCard({ scenario, isExpanded, onToggle, id }) {
  const accents = ["#4ecdc4", "#a78bfa", "#f87171"];
  const accent = accents[(scenario.id - 1) % accents.length];
  const bgColors = ["#0d2a2a", "#1a1028", "#2a1418"];
  const bg = bgColors[(scenario.id - 1) % bgColors.length];

  return (
    <div id={id} style={{
      background: bg,
      border: `1px solid ${isExpanded ? accent + "66" : accent + "22"}`,
      borderRadius: 10,
      overflow: "hidden",
      transition: "all 0.3s ease",
      boxShadow: isExpanded ? `0 0 40px ${accent}11` : "none",
    }}>
      {/* Header - always visible */}
      <div
        onClick={onToggle}
        style={{
          padding: "24px 28px",
          cursor: "pointer",
          userSelect: "none",
        }}
      >
        <div style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "flex-start",
          flexWrap: "wrap",
          gap: 12,
        }}>
          <div style={{ flex: 1, minWidth: 200 }}>
            <div style={{
              fontSize: 10,
              letterSpacing: "0.15em",
              color: accent,
              fontWeight: 700,
              textTransform: "uppercase",
              marginBottom: 6,
            }}>
              SCENARIO {scenario.id}
            </div>
            <h3 style={{
              fontSize: 20,
              fontWeight: 800,
              color: "#fff",
              margin: 0,
              letterSpacing: "0.04em",
            }}>
              {scenario.title}
            </h3>
          </div>
          <div style={{
            textAlign: "right",
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: 4,
          }}>
            <div style={{
              fontSize: 36,
              fontWeight: 800,
              color: accent,
              lineHeight: 1,
              fontVariantNumeric: "tabular-nums",
            }}>
              {scenario.probability}%
            </div>
            <div style={{
              fontSize: 11,
              color: "#6b7280",
              letterSpacing: "0.08em",
            }}>
              PROBABILITY
            </div>
          </div>
        </div>

        <ProbabilityBar probability={scenario.probability} accent={accent} />

        <div style={{
          marginTop: 16,
          display: "flex",
          gap: 16,
          alignItems: "center",
          flexWrap: "wrap",
        }}>
          <div style={{
            padding: "4px 12px",
            background: accent + "18",
            border: `1px solid ${accent}33`,
            borderRadius: 5,
            fontSize: 13,
            color: accent,
            fontWeight: 700,
            letterSpacing: "0.06em",
          }}>
            {scenario.voteSplit}
          </div>
          <div style={{
            fontSize: 12,
            color: "#9ca3af",
          }}>
            {scenario.author} writing for the majority
          </div>
        </div>

        {/* Vote dots */}
        <div style={{
          marginTop: 16,
          display: "flex",
          gap: 8,
          flexWrap: "wrap",
        }}>
          {[...scenario.majorityJustices, ...scenario.dissentJustices].map(j => (
            <VoteDot
              key={j}
              justice={j}
              inMajority={scenario.majorityJustices.includes(j)}
              accent={accent}
            />
          ))}
        </div>

        <p style={{
          fontSize: 13,
          color: "#b0b0bc",
          margin: "16px 0 0 0",
          lineHeight: 1.65,
        }}>
          {italicizeCaseNames(scenario.holding)}
        </p>

        <div style={{
          marginTop: 12,
          fontSize: 11,
          color: accent + "88",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}>
          {isExpanded ? "▲ COLLAPSE" : "▼ EXPAND FULL ANALYSIS"}
        </div>
      </div>

      {/* Expanded content */}
      {isExpanded && (
        <div style={{
          padding: "0 28px 28px",
          borderTop: `1px solid ${accent}15`,
        }}>
          {/* Primary Reasoning */}
          <div style={{ marginTop: 20 }}>
            <div style={{
              fontSize: 10,
              letterSpacing: "0.15em",
              color: accent,
              fontWeight: 700,
              textTransform: "uppercase",
              marginBottom: 14,
            }}>
              PRIMARY LEGAL REASONING
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {scenario.primaryReasoning.map((r, i) => (
                <div key={i} style={{
                  padding: "14px 18px",
                  background: "#ffffff05",
                  borderLeft: `3px solid ${accent}55`,
                  borderRadius: "0 6px 6px 0",
                }}>
                  <div style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: "#e2e2e8",
                    marginBottom: 6,
                    letterSpacing: "0.04em",
                  }}>
                    {r.label}
                  </div>
                  <div style={{
                    fontSize: 12,
                    color: "#9ca3af",
                    lineHeight: 1.6,
                  }}>
                    {italicizeCaseNames(r.summary)}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Concurrences */}
          {scenario.concurrences.length > 0 && (
            <div style={{ marginTop: 24 }}>
              <div style={{
                fontSize: 10,
                letterSpacing: "0.15em",
                color: "#facc15",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: 14,
              }}>
                CONCURRENCES
              </div>
              {scenario.concurrences.map((c, i) => (
                <div key={i} style={{
                  padding: "14px 18px",
                  background: "#facc1508",
                  border: "1px dashed #facc1522",
                  borderRadius: 6,
                  marginBottom: 10,
                }}>
                  <div style={{
                    fontSize: 12,
                    fontWeight: 700,
                    color: "#facc15",
                    marginBottom: 6,
                  }}>
                    {c.author}{c.joinedBy.length > 0 ? ` (joined by ${c.joinedBy.join(", ")})` : " (concurring in judgment)"}
                  </div>
                  <div style={{ fontSize: 12, color: "#9ca3af", lineHeight: 1.6 }}>
                    {italicizeCaseNames(c.summary)}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Dissent */}
          <div style={{ marginTop: 24 }}>
            <div style={{
              fontSize: 10,
              letterSpacing: "0.15em",
              color: "#f87171",
              fontWeight: 700,
              textTransform: "uppercase",
              marginBottom: 14,
            }}>
              DISSENT
            </div>
            <div style={{
              padding: "14px 18px",
              background: "#f8717108",
              border: "1px solid #f8717122",
              borderRadius: 6,
            }}>
              <div style={{
                fontSize: 12,
                fontWeight: 700,
                color: "#f87171",
                marginBottom: 10,
              }}>
                {scenario.dissent.author} (joined by {scenario.dissent.joinedBy.join(", ")})
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {scenario.dissent.coreArguments.map((arg, i) => (
                  <div key={i} style={{
                    fontSize: 12,
                    color: "#9ca3af",
                    lineHeight: 1.6,
                    paddingLeft: 12,
                    borderLeft: "2px solid #f8717133",
                  }}>
                    {italicizeCaseNames(arg)}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* New Rule */}
          <div style={{ marginTop: 24 }}>
            <div style={{
              fontSize: 10,
              letterSpacing: "0.15em",
              color: "#4ade80",
              fontWeight: 700,
              textTransform: "uppercase",
              marginBottom: 14,
            }}>
              WHAT CHANGES GOING FORWARD
            </div>
            <div style={{
              padding: "14px 18px",
              background: "#4ade8008",
              border: "1px solid #4ade8022",
              borderRadius: 6,
              fontSize: 12,
              color: "#9ca3af",
              lineHeight: 1.6,
            }}>
              {italicizeCaseNames(scenario.newRule)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function JusticeRow({ vote }) {
  const meta = JUSTICES_META[vote.name];
  const wingColor = WING_COLORS[meta.wing];
  const isAgainst = vote.prediction.toLowerCase().includes("against");
  const predColor = isAgainst ? "#4ecdc4" : "#fb923c";

  return (
    <div style={{
      padding: "16px 20px",
      background: "#ffffff04",
      borderRadius: 8,
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: 8,
        flexWrap: "wrap",
        gap: 8,
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}>
          <div style={{
            fontSize: 15,
            fontWeight: 700,
            color: "#e2e2e8",
            letterSpacing: "0.03em",
          }}>
            {vote.name}
          </div>
          <div style={{
            fontSize: 10,
            color: wingColor,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
          }}>
            {meta.wing}
          </div>
        </div>
        <div style={{
          display: "flex",
          gap: 10,
          alignItems: "center",
        }}>
          <span style={{
            padding: "3px 10px",
            background: predColor + "18",
            border: `1px solid ${predColor}44`,
            borderRadius: 4,
            fontSize: 11,
            fontWeight: 700,
            color: predColor,
            letterSpacing: "0.04em",
          }}>
            {vote.prediction}
          </span>
          <span style={{
            fontSize: 11,
            color: "#6b7280",
            letterSpacing: "0.06em",
          }}>
            Confidence: {vote.confidence}
          </span>
        </div>
      </div>
      <div style={{
        fontSize: 12,
        color: "#9ca3af",
        lineHeight: 1.6,
      }}>
        {italicizeCaseNames(vote.reasoning)}
      </div>
    </div>
  );
}

export default function SCOTUSPredictor() {
  const [expandedScenario, setExpandedScenario] = useState(null);
  const [activeTab, setActiveTab] = useState("scenarios");
  const [activeCaseIdx, setActiveCaseIdx] = useState(0);

  const caseData = CASES[activeCaseIdx];

  return (
    <div style={{
      minHeight: "100vh",
      background: "#08080d",
      color: "#e2e2e8",
      fontFamily: "'JetBrains Mono', 'SF Mono', 'Fira Code', 'Consolas', monospace",
    }}>
      {/* Top Bar */}
      <div style={{
        borderBottom: "1px solid #ffffff0a",
        padding: "14px 24px",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexWrap: "wrap",
        gap: 12,
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}>
          <div style={{
            width: 8,
            height: 8,
            borderRadius: "50%",
            background: "#4ecdc4",
            boxShadow: "0 0 8px #4ecdc466",
          }} />
          <span style={{
            fontSize: 13,
            fontWeight: 800,
            letterSpacing: "0.12em",
            textTransform: "uppercase",
            color: "#fff",
          }}>
            SCOTUS PREDICTOR
          </span>
        </div>
        <div style={{
          fontSize: 10,
          color: "#4b5563",
          letterSpacing: "0.1em",
          textTransform: "uppercase",
        }}>
          AI-ASSISTED PREDICTION · V1.0
        </div>
      </div>

      <div style={{
        maxWidth: 960,
        margin: "0 auto",
        padding: "32px 20px 80px",
      }}>
        {/* Case Selector (for multi-case) */}
        {CASES.length > 1 && (
          <div style={{
            display: "flex",
            gap: 8,
            marginBottom: 24,
            flexWrap: "wrap",
          }}>
            {CASES.map((c, i) => (
              <button
                key={c.id}
                onClick={() => { setActiveCaseIdx(i); setExpandedScenario(null); }}
                style={{
                  padding: "8px 16px",
                  background: i === activeCaseIdx ? "#4ecdc418" : "#ffffff06",
                  border: `1px solid ${i === activeCaseIdx ? "#4ecdc4" : "#ffffff11"}`,
                  color: i === activeCaseIdx ? "#4ecdc4" : "#6b7280",
                  borderRadius: 6,
                  cursor: "pointer",
                  fontSize: 11,
                  fontFamily: "inherit",
                  letterSpacing: "0.05em",
                }}
              >
                {c.name}
              </button>
            ))}
          </div>
        )}

        {/* Case Header */}
        <div style={{ marginBottom: 36 }}>
          <div style={{
            display: "flex",
            gap: 10,
            alignItems: "center",
            marginBottom: 12,
            flexWrap: "wrap",
          }}>
            <span style={{
              padding: "4px 10px",
              background: "#22d3ee18",
              border: "1px solid #22d3ee44",
              borderRadius: 4,
              fontSize: 10,
              color: "#22d3ee",
              fontWeight: 700,
              letterSpacing: "0.1em",
            }}>
              {caseData.status.toUpperCase()}
            </span>
            <span style={{
              fontSize: 10,
              color: "#4b5563",
              letterSpacing: "0.08em",
            }}>
              {caseData.docket} · {caseData.term}
            </span>
          </div>

          <h1 style={{
            fontSize: 28,
            fontWeight: 800,
            color: "#fff",
            margin: "0 0 8px 0",
            letterSpacing: "0.02em",
            lineHeight: 1.2,
          }}>
            {caseData.name}
          </h1>

          <p style={{
            fontSize: 14,
            color: "#9ca3af",
            margin: "0 0 16px 0",
            lineHeight: 1.6,
            maxWidth: 700,
          }}>
            {caseData.questionPresented}
          </p>

          <div style={{
            display: "flex",
            gap: 20,
            fontSize: 11,
            color: "#4b5563",
            letterSpacing: "0.06em",
            flexWrap: "wrap",
          }}>
            <span>Argued: {caseData.argued}</span>
            <span>Last updated: {caseData.lastUpdated}</span>
          </div>
        </div>

        {/* Tabs */}
        <div style={{
          display: "flex",
          gap: 0,
          marginBottom: 28,
          borderBottom: "1px solid #ffffff0a",
        }}>
          {[
            { id: "scenarios", label: "Outcome Scenarios" },
            { id: "justices", label: "Justice-by-Justice" },
            { id: "methodology", label: "Methodology" },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                padding: "12px 20px",
                background: "transparent",
                border: "none",
                borderBottom: `2px solid ${activeTab === tab.id ? "#4ecdc4" : "transparent"}`,
                color: activeTab === tab.id ? "#4ecdc4" : "#6b7280",
                fontSize: 12,
                fontWeight: 700,
                letterSpacing: "0.08em",
                textTransform: "uppercase",
                cursor: "pointer",
                fontFamily: "inherit",
                transition: "all 0.2s ease",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Scenarios Tab */}
        {activeTab === "scenarios" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {/* Stacked probability bar */}
            <div style={{
              padding: "20px 24px",
              background: "#ffffff04",
              border: "1px solid #ffffff0a",
              borderRadius: 8,
              marginBottom: 8,
            }}>
              <div style={{
                fontSize: 10,
                letterSpacing: "0.12em",
                color: "#6b7280",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: 12,
              }}>
                OUTCOME PROBABILITIES
              </div>
              <div style={{
                display: "flex",
                width: "100%",
                height: 32,
                borderRadius: 6,
                overflow: "hidden",
                gap: 2,
              }}>
                {caseData.scenarios.map((s, i) => {
                  const accents = ["#4ecdc4", "#a78bfa", "#f87171"];
                  return (
                    <div key={s.id} style={{
                      width: `${s.probability}%`,
                      height: "100%",
                      background: accents[i] + "33",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontSize: 12,
                      fontWeight: 800,
                      color: accents[i],
                      transition: "width 0.8s ease",
                      cursor: "pointer",
                    }}
                    onClick={() => {
                      setExpandedScenario(expandedScenario === s.id ? null : s.id);
                      setTimeout(() => {
                        const el = document.getElementById(`scenario-${s.id}`);
                        if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
                      }, 100);
                    }}
                    >
                      {s.probability}%
                    </div>
                  );
                })}
              </div>
              <div style={{
                display: "flex",
                justifyContent: "space-between",
                marginTop: 10,
                flexWrap: "wrap",
                gap: 8,
              }}>
                {caseData.scenarios.map((s, i) => {
                  const accents = ["#4ecdc4", "#a78bfa", "#f87171"];
                  return (
                    <div key={s.id} style={{
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                    }}>
                      <div style={{
                        width: 8,
                        height: 8,
                        borderRadius: 2,
                        background: accents[i],
                      }} />
                      <span style={{
                        fontSize: 11,
                        color: "#9ca3af",
                        letterSpacing: "0.04em",
                      }}>
                        {s.shortLabel} ({s.voteSplit})
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>

            {caseData.scenarios.map(s => (
              <ScenarioCard
                key={s.id}
                scenario={s}
                isExpanded={expandedScenario === s.id}
                onToggle={() => setExpandedScenario(expandedScenario === s.id ? null : s.id)}
                id={`scenario-${s.id}`}
              />
            ))}
          </div>
        )}

        {/* Justices Tab */}
        {activeTab === "justices" && (
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            <div style={{
              padding: "14px 20px",
              background: "#4ecdc408",
              border: "1px solid #4ecdc422",
              borderRadius: 8,
              marginBottom: 8,
            }}>
              <div style={{
                fontSize: 12,
                color: "#4ecdc4",
                fontWeight: 700,
                marginBottom: 4,
              }}>
                PREDICTED OUTCOME
              </div>
              <div style={{
                fontSize: 14,
                color: "#e2e2e8",
              }}>
                6–3 or 7–2 against the government. Thomas, Alito likely dissent. Kavanaugh is the swing — if he joins the majority, it's 7–2.
              </div>
            </div>
            {caseData.justiceVotes.map(v => (
              <JusticeRow key={v.name} vote={v} />
            ))}
          </div>
        )}

        {/* Methodology Tab */}
        {activeTab === "methodology" && (
          <div style={{
            display: "flex",
            flexDirection: "column",
            gap: 16,
            fontSize: 13,
            color: "#9ca3af",
            lineHeight: 1.7,
          }}>
            <div style={{
              padding: "20px 24px",
              background: "#ffffff04",
              borderRadius: 8,
              border: "1px solid #ffffff0a",
            }}>
              <div style={{
                fontSize: 11,
                letterSpacing: "0.12em",
                color: "#4ecdc4",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: 12,
              }}>
                HOW THIS WORKS
              </div>
              <p style={{ margin: "0 0 12px 0" }}>
                Each prediction is generated by a multi-step analytical pipeline using Claude (Anthropic's AI) with extensive primary legal source material. The pipeline processes Supreme Court opinions cited in party briefs, oral argument transcripts, selected amicus briefs, and statistical voting data from the Supreme Court Database.
              </p>
              <p style={{ margin: "0 0 12px 0" }}>
                Each justice is analyzed individually with their own relevant prior writings, then results are synthesized into coherent outcome scenarios with probability estimates.
              </p>
              <p style={{ margin: 0 }}>
                The system uses primary legal sources — actual opinions, actual transcripts, actual briefs — not media coverage, punditry, or secondary analysis.
              </p>
            </div>

            <div style={{
              padding: "20px 24px",
              background: "#ffffff04",
              borderRadius: 8,
              border: "1px solid #ffffff0a",
            }}>
              <div style={{
                fontSize: 11,
                letterSpacing: "0.12em",
                color: "#a78bfa",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: 12,
              }}>
                PIPELINE STEPS
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {[
                  "Automated extraction of cited cases from party and selected amicus briefs",
                  "Download and summarization of cited opinions, preserving doctrinal holdings and vote breakdowns",
                  "Integration of SCDB statistical voting data for the current natural court and relevant issue areas",
                  "Issue analysis: identifying the doctrinal questions that will determine the outcome",
                  "Per-justice vote prediction (9 separate API calls, each with justice-specific prior writings + full case context)",
                  "Scenario construction: synthesizing 9 predictions into coherent outcome paths with probabilities",
                  "Opinion drafting: generating majority, concurrence, and dissent texts in authentic judicial voice",
                ].map((step, i) => (
                  <div key={i} style={{
                    display: "flex",
                    gap: 12,
                    alignItems: "flex-start",
                  }}>
                    <span style={{
                      fontSize: 10,
                      color: "#a78bfa",
                      fontWeight: 700,
                      minWidth: 16,
                      paddingTop: 2,
                    }}>
                      {i + 1}.
                    </span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              padding: "20px 24px",
              background: "#ffffff04",
              borderRadius: 8,
              border: "1px solid #ffffff0a",
            }}>
              <div style={{
                fontSize: 11,
                letterSpacing: "0.12em",
                color: "#facc15",
                fontWeight: 700,
                textTransform: "uppercase",
                marginBottom: 12,
              }}>
                DATA SOURCES
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {[
                  "Supreme Court Database (SCDB) — Washington University",
                  "CourtListener — Free Law Project",
                  "Supreme Court official filings — supremecourt.gov",
                  "Oral argument transcripts — supremecourt.gov / Oyez",
                  "Full opinion texts for all cases cited in party briefs",
                ].map((src, i) => (
                  <div key={i} style={{
                    fontSize: 12,
                    color: "#9ca3af",
                    paddingLeft: 12,
                    borderLeft: "2px solid #facc1533",
                  }}>
                    {src}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Disclaimer */}
        <div style={{
          marginTop: 40,
          padding: "18px 22px",
          background: "#f8717108",
          border: "1px solid #f8717122",
          borderRadius: 8,
          fontSize: 11,
          color: "#9ca3af",
          lineHeight: 1.6,
        }}>
          <span style={{ color: "#f87171", fontWeight: 700, letterSpacing: "0.08em" }}>
            DISCLAIMER
          </span>{" "}
          This is an AI-assisted prediction for educational and analytical purposes. It is not legal advice. Citations should be independently verified. Predictions reflect analytical modeling, not certainty. This tool is experimental and under active development.
        </div>
      </div>
    </div>
  );
}
