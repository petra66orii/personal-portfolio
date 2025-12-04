import { useState } from "react";
import {
  Shield,
  Zap,
  Search,
  AlertTriangle,
  FileText,
  CheckCircle,
  XCircle,
  Activity,
  Globe,
  ArrowRight,
} from "lucide-react";

/* --- TYPES --- */

interface SSLData {
  days_remaining: number;
  status: "Good" | "Critical" | "Error";
}

interface LighthouseData {
  performance_score: number;
  accessibility_score: number;
  seo_score: number;
  core_web_vitals: string;
}

interface HealthData {
  title_tag: string;
  meta_description: string;
  h1_tag: string;
  mobile_viewport: string;
  broken_links_found: number;
  broken_link_examples: string[];
}

interface TechnicalData {
  ssl: SSLData;
  lighthouse: LighthouseData;
  health: HealthData;
}

interface AuditResponse {
  technical_data: TechnicalData;
  email_draft: string;
}

declare global {
  interface Window {
    DJANGO_CSRF_TOKEN: string;
  }
}

export default function AuditDashboard() {
  const [url, setUrl] = useState("https://popflexactive.com");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditResponse | null>(null);
  const [activeTab, setActiveTab] = useState<"audit" | "proposal">("audit");
  const [error, setError] = useState<string | null>(null);

  const startAudit = async () => {
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const csrfToken = window.DJANGO_CSRF_TOKEN;

      const response = await fetch("/api/run-audit/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(
          `Audit failed: ${response.status} ${response.statusText}`
        );
      }

      const data: AuditResponse = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="py-8 px-4">
      <div className="max-w-5xl mx-auto">
        {/* ————————————————
            CLEAN WHITE PRIMARY CONTAINER
            ———————————————— */}
        <div className="admin-reset bg-white rounded-3xl shadow-xl border border-slate-200 p-6 md:p-8">
          {/* HEADER */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center pb-6 border-b border-slate-200">
            <div>
              <p className="text-[11px] font-semibold tracking-[0.25em] text-slate-500 uppercase">
                Client Intelligence
              </p>

              <h1 className="mt-2 text-3xl md:text-4xl font-bold logo-gradient bg-clip-text text-transparent">
                Digital Asset Intelligence
              </h1>

              <div className="h-1 w-24 rounded-full mt-2 button-gradient" />

              <p className="mt-2 text-sm text-slate-500">
                Miss Bott · Technical Auditor & Solutions Architect
              </p>
            </div>

            {/* URL + CTA */}
            <div className="mt-4 md:mt-0 w-full md:w-auto">
              <div className="flex items-center bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <span className="pl-3 pr-1 text-slate-400">
                  <Globe className="w-4 h-4" />
                </span>

                <input
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1 bg-transparent px-2 py-2 text-sm text-slate-800 placeholder:text-slate-400 outline-none"
                  placeholder="https://target-site.com"
                />

                <button
                  onClick={startAudit}
                  disabled={loading}
                  className={`h-full px-4 py-2 text-xs font-medium flex items-center gap-2 button-gradient text-white transition-all
                    ${
                      loading
                        ? "opacity-70 cursor-not-allowed"
                        : "hover:opacity-90"
                    }`}
                >
                  {loading ? (
                    <>
                      <Activity className="w-4 h-4 animate-spin" />
                      Auditing…
                    </>
                  ) : (
                    <>
                      Run Diagnostics
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>

              <p className="mt-1 text-[11px] text-slate-500">
                Uses live Lighthouse + SSL intelligence. Great for pre-sales.
              </p>
            </div>
          </div>

          {/* ERROR */}
          {error && (
            <div className="mt-4 bg-red-50 text-red-700 p-4 rounded-lg border border-red-200 flex gap-3 text-sm">
              <AlertTriangle className="w-5 h-5" />
              <div>
                <p className="font-semibold">Audit failed</p>
                <p>{error}</p>
              </div>
            </div>
          )}

          {/* RESULTS */}
          {result && (
            <div className="mt-6">
              {/* TABS */}
              <div className="inline-flex items-center bg-slate-100 rounded-full p-1 mb-6">
                <TabButton
                  active={activeTab === "audit"}
                  onClick={() => setActiveTab("audit")}
                >
                  Technical Findings
                </TabButton>
                <TabButton
                  active={activeTab === "proposal"}
                  onClick={() => setActiveTab("proposal")}
                >
                  Strategic Proposal (AI)
                </TabButton>
              </div>

              {/* ——— AUDIT TAB ——— */}
              {activeTab === "audit" && (
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                  {/* LEFT COLUMN */}
                  <div className="md:col-span-8 space-y-6">
                    {/* LIGHTHOUSE */}
                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-8 h-8 rounded-full flex items-center justify-center button-gradient text-white shadow-sm">
                          <Zap className="w-4 h-4" />
                        </div>
                        <div>
                          <h2 className="text-sm font-semibold text-slate-900">
                            Core Web Vitals (Lighthouse)
                          </h2>
                          <p className="text-xs text-slate-500">
                            Performance, accessibility, SEO snapshot
                          </p>
                        </div>
                      </div>

                      <div className="grid sm:grid-cols-3 gap-4">
                        <ScoreGauge
                          label="Performance"
                          score={
                            result.technical_data.lighthouse.performance_score
                          }
                        />
                        <ScoreGauge
                          label="Accessibility"
                          score={
                            result.technical_data.lighthouse.accessibility_score
                          }
                        />
                        <ScoreGauge
                          label="SEO"
                          score={result.technical_data.lighthouse.seo_score}
                        />
                      </div>

                      <div className="mt-6 bg-slate-50 border border-slate-200 p-4 rounded-lg text-sm">
                        <p className="text-xs font-semibold uppercase text-slate-500">
                          Analyst Note
                        </p>
                        <p className="text-slate-700 mt-1">
                          {result.technical_data.lighthouse.performance_score <
                          50
                            ? "Severe performance degradation detected. High mobile bounce probability."
                            : "Performance is acceptable but shows signs of heavy script overhead."}
                        </p>
                      </div>
                    </div>

                    {/* HEALTH */}
                    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                      <div className="flex items-center gap-2 mb-4">
                        <Activity className="w-4 h-4 text-blue-500" />
                        <h2 className="text-sm font-semibold text-slate-900">
                          Site Health & Integrity
                        </h2>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4">
                        <HealthItem
                          label="Title Tag"
                          value={result.technical_data.health.title_tag}
                        />
                        <HealthItem
                          label="Meta Description"
                          value={result.technical_data.health.meta_description}
                        />
                        <HealthItem
                          label="H1 Structure"
                          value={result.technical_data.health.h1_tag}
                        />
                        <HealthItem
                          label="Mobile Viewport"
                          value={result.technical_data.health.mobile_viewport}
                        />
                      </div>

                      {result.technical_data.health.broken_links_found > 0 && (
                        <div className="mt-6 border-t border-slate-200 pt-4">
                          <div className="flex items-center text-red-600 font-medium text-sm mb-2">
                            <AlertTriangle className="w-4 h-4 mr-1" />
                            {
                              result.technical_data.health.broken_links_found
                            }{" "}
                            Broken Internal Links
                          </div>
                          <ul className="text-xs text-slate-600 ml-6 list-disc space-y-1">
                            {result.technical_data.health.broken_link_examples.map(
                              (link, i) => (
                                <li key={i} className="truncate">
                                  {link}
                                </li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* RIGHT COLUMN */}
                  <div className="md:col-span-4 space-y-6">
                    {/* SSL */}
                    <div
                      className={`p-6 rounded-xl border shadow-sm ${
                        result.technical_data.ssl.status === "Critical"
                          ? "bg-red-50 border-red-200"
                          : "bg-emerald-50 border-emerald-200"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <Shield
                          className={`w-5 h-5 ${
                            result.technical_data.ssl.status === "Critical"
                              ? "text-red-600"
                              : "text-emerald-600"
                          }`}
                        />
                        <h2 className="text-sm font-semibold text-slate-900">
                          Security Status
                        </h2>
                      </div>

                      <div className="text-3xl font-bold text-slate-900">
                        {result.technical_data.ssl.days_remaining} days
                      </div>

                      <p className="text-xs text-slate-600 mt-1">
                        SSL Certificate Remaining
                      </p>

                      {result.technical_data.ssl.status === "Critical" && (
                        <p className="mt-3 inline-flex items-center text-[11px] font-semibold text-red-700 bg-white px-2 py-1 rounded-full">
                          <AlertTriangle className="w-3 h-3 mr-1" />
                          Renewal Required
                        </p>
                      )}
                    </div>

                    {/* MIGRATION */}
                    <div className="rounded-xl p-6 bg-gradient-to-br from-purple-300 to-pink-300 text-slate-900 shadow-lg">
                      <h3 className="text-xs uppercase tracking-wide mb-3 font-semibold opacity-80">
                        Migration Feasibility
                      </h3>

                      <div className="flex justify-between text-sm mb-2">
                        <span>Technical Debt Load</span>
                        <span className="font-bold">High</span>
                      </div>

                      <div className="w-full bg-white/40 h-2 rounded-full mb-3">
                        <div
                          className="h-2 bg-white rounded-full"
                          style={{ width: "85%" }}
                        />
                      </div>

                      <p className="text-xs leading-relaxed opacity-90">
                        Current stack shows monolithic limitations (WP/Magento).
                        A headless React/Django migration is recommended.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* ——— PROPOSAL TAB ——— */}
              {activeTab === "proposal" && (
                <div className="bg-white p-6 md:p-8 rounded-xl shadow-sm border border-slate-200">
                  <div className="flex justify-between items-center mb-4">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-purple-500" />
                      <h2 className="text-base font-semibold text-slate-900">
                        Strategic Proposal Draft
                      </h2>
                    </div>

                    <button
                      onClick={() =>
                        navigator.clipboard.writeText(result.email_draft)
                      }
                      className="text-xs text-slate-500 hover:text-purple-600 transition flex items-center gap-1"
                    >
                      Copy
                      <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>

                  <textarea
                    readOnly
                    value={result.email_draft}
                    className="w-full h-96 p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-800 font-mono outline-none focus:ring-2 focus:ring-purple-400 resize-none"
                  />
                </div>
              )}
            </div>
          )}

          {/* EMPTY STATE */}
          {!result && !loading && (
            <div className="mt-10 text-center py-16 bg-white rounded-xl border border-dashed border-slate-300">
              <Search className="w-10 h-10 text-slate-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-slate-900">
                Ready when you are
              </h3>
              <p className="text-sm text-slate-500 max-w-md mx-auto mt-2">
                Enter any live URL to generate a technical audit + proposal.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ————————————
   SUBCOMPONENTS
———————————— */

function TabButton({
  active,
  children,
  onClick,
}: {
  active: boolean;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-1.5 text-xs md:text-sm font-medium rounded-full transition-all ${
        active
          ? "bg-white shadow text-slate-900"
          : "text-slate-500 hover:text-slate-800"
      }`}
    >
      {children}
    </button>
  );
}

interface ScoreGaugeProps {
  label: string;
  score: number;
}

function ScoreGauge({ label, score }: ScoreGaugeProps) {
  const color =
    score >= 90
      ? "bg-emerald-50 border-emerald-300 text-emerald-700"
      : score >= 50
      ? "bg-amber-50 border-amber-300 text-amber-700"
      : "bg-red-50 border-red-300 text-red-700";

  return (
    <div className="flex flex-col items-center p-3">
      <div
        className={`w-20 h-20 rounded-full border-[3px] flex items-center justify-center text-2xl font-semibold ${color}`}
      >
        {score}
      </div>

      <span className="mt-2 text-xs font-medium text-slate-600">{label}</span>
    </div>
  );
}

interface HealthItemProps {
  label: string;
  value: string;
}

function HealthItem({ label, value }: HealthItemProps) {
  const isGood = value === "Good";

  return (
    <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-lg border border-slate-200">
      <span className="text-xs font-medium text-slate-700">{label}</span>

      <div className="flex items-center">
        {isGood ? (
          <CheckCircle className="w-4 h-4 text-emerald-600 mr-1.5" />
        ) : (
          <XCircle className="w-4 h-4 text-red-600 mr-1.5" />
        )}

        <span
          className={`text-[11px] font-semibold uppercase ${
            isGood ? "text-emerald-700" : "text-red-700"
          }`}
        >
          {value}
        </span>
      </div>
    </div>
  );
}
