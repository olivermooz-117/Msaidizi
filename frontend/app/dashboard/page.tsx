"use client";

import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  Bot,
  BookOpen,
  Check,
  ChevronDown,
  CircleHelp,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  MessageCircle,
  Plus,
  Search,
  Send,
  Settings,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  X,
  Zap
} from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  addDocument,
  getDocuments,
  type DocumentItem
} from "@/lib/api";

const navigation = [
  { label: "Overview", icon: LayoutDashboard, active: true },
  { label: "Conversations", icon: MessageCircle },
  { label: "Knowledge base", icon: BookOpen },
  { label: "AI assistant", icon: Bot }
];

export default function Dashboard() {
  const router = useRouter();

  const [token, setToken] = useState("");
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");

  useEffect(() => {
    const savedToken = localStorage.getItem("msaidizi_token");

    if (!savedToken) {
      router.replace("/login");
      return;
    }

    setToken(savedToken);

    getDocuments(savedToken)
      .then(setDocuments)
      .catch((err) => {
        if (err instanceof Error && err.message.toLowerCase().includes("invalid email or password")) {
          localStorage.removeItem("msaidizi_token");
          router.replace("/login");
          return;
        }

        setError(err instanceof Error ? err.message : "Unable to load your knowledge base.");
      })
      .finally(() => setLoading(false));
  }, [router]);

  async function handleAddDocument(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token || !title.trim() || !content.trim()) return;

    setSaving(true);
    setError("");

    try {
      await addDocument(token, title.trim(), content.trim());
      const updated = await getDocuments(token);
      setDocuments(updated);
      setTitle("");
      setContent("");
      setShowAdd(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not add document.");
    } finally {
      setSaving(false);
    }
  }

  function logout() {
    localStorage.removeItem("msaidizi_token");
    router.replace("/login");
  }

  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <div className="ambient ambient-three" />

      <aside className={`sidebar glass-panel ${mobileNav ? "sidebar-open" : ""}`}>
        <div className="brand">
          <div className="brand-mark"><Sparkles size={21} /></div>
          <span>msaidizi<span className="brand-dot">.</span></span>
          <button className="mobile-close icon-button" onClick={() => setMobileNav(false)}>
            <X size={19} />
          </button>
        </div>

        <div className="workspace-switcher glass-inset">
          <div className="workspace-avatar">N</div>
          <div className="workspace-copy">
            <strong>Nairobi Threads</strong>
            <span>Business workspace</span>
          </div>
          <ChevronDown size={16} className="muted-icon" />
        </div>

        <div className="nav-label">WORKSPACE</div>
        <nav className="main-nav">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.label}
                href={item.label === "Knowledge base" ? "#knowledge" : "#overview"}
                className={`nav-item ${item.active ? "nav-active" : ""}`}
                onClick={() => setMobileNav(false)}
              >
                <Icon size={18} strokeWidth={1.8} />
                <span>{item.label}</span>
                {item.label === "Conversations" && <span className="nav-count">4</span>}
              </a>
            );
          })}
        </nav>

        <div className="nav-label nav-label-spaced">PREFERENCES</div>
        <nav className="main-nav">
          <a href="#settings" className="nav-item">
            <Settings size={18} /><span>Settings</span>
          </a>
          <a href="#help" className="nav-item">
            <CircleHelp size={18} /><span>Help centre</span>
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="plan-card glass-inset">
            <div className="plan-icon"><Zap size={17} /></div>
            <div>
              <strong>Workspace status</strong>
              <span>You're all set up</span>
            </div>
            <span className="status-dot" />
          </div>

          <button className="profile-row" onClick={logout}>
            <div className="profile-avatar">O</div>
            <div className="profile-copy">
              <strong>Workspace owner</strong>
              <span>Sign out</span>
            </div>
            <LogOut size={17} className="muted-icon" />
          </button>
        </div>
      </aside>

      {mobileNav && <button className="mobile-scrim" onClick={() => setMobileNav(false)} />}

      <section className="main-area">
        <header className="topbar glass-panel">
          <div className="topbar-left">
            <button className="mobile-menu icon-button" onClick={() => setMobileNav(true)}>
              <Menu size={20} />
            </button>
            <div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div>
          </div>

          <div className="topbar-right">
            <div className="system-status"><span className="status-dot" /> All systems operational</div>
            <button className="top-icon icon-button" aria-label="Search"><Search size={18} /></button>
            <div className="top-avatar">O</div>
          </div>
        </header>

        <div className="content" id="overview">
          <div className="welcome-row">
            <div>
              <div className="eyebrow"><span className="eyebrow-line" /> YOUR AI WORKSPACE</div>
              <h1>Good afternoon<span className="heading-period">.</span></h1>
              <p className="welcome-subtitle">
                Here&apos;s what&apos;s happening with your customer experience.
              </p>
            </div>
            <button className="primary-button" onClick={() => setShowAdd(true)}>
              <Plus size={18} /> Add knowledge
            </button>
          </div>

          {error && (
            <div className="error-banner">
              <CircleHelp size={17} />
              <span>{error}</span>
              <button onClick={() => setError("")}><X size={16} /></button>
            </div>
          )}

          <div className="metrics-grid">
            <MetricCard
              label="Conversations"
              value="1,284"
              change="+12.8%"
              note="vs. last month"
              icon={<MessageCircle size={19} />}
              trend="up"
            />
            <MetricCard
              label="AI resolution rate"
              value="87.4%"
              change="+5.2%"
              note="vs. last month"
              icon={<ShieldCheck size={19} />}
              trend="up"
            />
            <MetricCard
              label="Average response"
              value="1.8s"
              change="-0.4s"
              note="faster this month"
              icon={<Zap size={19} />}
              trend="up"
            />
            <MetricCard
              label="Customer satisfaction"
              value="96.2%"
              change="+2.1%"
              note="vs. last month"
              icon={<Activity size={19} />}
              trend="up"
            />
          </div>

          <div className="dashboard-grid">
            <section className="glass-panel hero-card">
              <div className="hero-glow" />
              <div className="hero-content">
                <div className="hero-topline">
                  <span className="ai-pill"><Sparkles size={13} /> AI ASSISTANT</span>
                  <span className="live-label"><span className="status-dot" /> LIVE</span>
                </div>
                <div className="hero-heading">
                  <div>
                    <h2>Your support,<br />on autopilot.</h2>
                    <p>
                      Msaidizi is ready to help your customers, answer questions
                      and keep your business moving.
                    </p>
                  </div>
                  <div className="orbital-art" aria-hidden="true">
                    <div className="orbital-ring ring-one" />
                    <div className="orbital-ring ring-two" />
                    <div className="orbital-core"><Bot size={39} /></div>
                    <span className="orbit-spark spark-one">✦</span>
                    <span className="orbit-spark spark-two">✧</span>
                  </div>
                </div>
                <div className="hero-footer">
                  <div className="hero-foot-note"><span className="status-dot" /> Assistant is ready</div>
                  <a href="#knowledge" className="text-link">Manage knowledge <ArrowUpRight size={15} /></a>
                </div>
              </div>
            </section>

            <section className="glass-panel activity-card">
              <div className="section-heading">
                <div>
                  <span className="section-kicker">ACTIVITY</span>
                  <h3>Recent activity</h3>
                </div>
                <button className="subtle-button">This week <ChevronDown size={14} /></button>
              </div>
              <div className="activity-list">
                <ActivityItem
                  icon={<MessageCircle size={16} />}
                  title="New conversation"
                  detail="Customer asked about delivery"
                  time="2 min ago"
                  tone="violet"
                />
                <ActivityItem
                  icon={<Check size={16} />}
                  title="Question resolved"
                  detail="Return policy · AI assistant"
                  time="18 min ago"
                  tone="green"
                />
                <ActivityItem
                  icon={<FileText size={16} />}
                  title="Knowledge updated"
                  detail="Product catalogue synced"
                  time="1 hour ago"
                  tone="blue"
                />
                <ActivityItem
                  icon={<ArrowDownRight size={16} />}
                  title="Human handoff"
                  detail="Customer requested an agent"
                  time="3 hours ago"
                  tone="orange"
                />
              </div>
            </section>
          </div>

          <section className="glass-panel knowledge-section" id="knowledge">
            <div className="section-heading knowledge-heading">
              <div>
                <span className="section-kicker">YOUR CONTENT</span>
                <h3>Knowledge base</h3>
                <p>Give your AI assistant the context it needs to help customers.</p>
              </div>
              <button className="secondary-button" onClick={() => setShowAdd(true)}>
                <Plus size={16} /> Add document
              </button>
            </div>

            <div className="knowledge-summary">
              <div className="knowledge-summary-icon"><BookOpen size={19} /></div>
              <div>
                <strong>{documents.length} documents</strong>
                <span>Available to your AI assistant</span>
              </div>
              <div className="knowledge-summary-spacer" />
              <span className="sync-indicator"><span className="status-dot" /> Connected</span>
            </div>

            {loading ? (
              <div className="empty-state"><div className="loader" /> Loading your documents...</div>
            ) : documents.length > 0 ? (
              <div className="document-list">
                {documents.map((doc) => (
                  <div className="document-row" key={doc.id}>
                    <div className="document-icon"><FileText size={18} /></div>
                    <div className="document-info">
                      <strong>{doc.title}</strong>
                      <span>{doc.source_type || "Document"} · Available to assistant</span>
                    </div>
                    <span className="document-status"><span className="status-dot" /> Ready</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon"><UploadCloud size={25} /></div>
                <strong>Your knowledge base starts here</strong>
                <span>Add FAQs, product information or business policies.</span>
                <button className="secondary-button" onClick={() => setShowAdd(true)}>
                  <Plus size={16} /> Add your first document
                </button>
              </div>
            )}
          </section>

          <footer className="page-footer">
            <span>© 2026 Msaidizi AI</span>
            <span>Built for better conversations <Sparkles size={13} /></span>
          </footer>
        </div>
      </section>

      {showAdd && (
        <div className="modal-backdrop" onClick={() => setShowAdd(false)}>
          <div className="glass-panel modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-heading">
              <div>
                <span className="section-kicker">KNOWLEDGE BASE</span>
                <h3>Add a document</h3>
                <p>Give your assistant information it can use to answer customers.</p>
              </div>
              <button className="icon-button" onClick={() => setShowAdd(false)}><X size={19} /></button>
            </div>
            <form onSubmit={handleAddDocument}>
              <label htmlFor="doc-title">Document title</label>
              <input
                id="doc-title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Delivery and returns policy"
                required
              />
              <label htmlFor="doc-content">Document content</label>
              <textarea
                id="doc-content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Paste your FAQs, policies or product information here..."
                rows={7}
                required
              />
              <div className="modal-actions">
                <button type="button" className="secondary-button" onClick={() => setShowAdd(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary-button" disabled={saving}>
                  {saving ? "Saving..." : <><Send size={16} /> Save document</>}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

function MetricCard({
  label,
  value,
  change,
  note,
  icon,
  trend
}: {
  label: string;
  value: string;
  change: string;
  note: string;
  icon: React.ReactNode;
  trend: "up" | "down";
}) {
  return (
    <div className="glass-panel metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <div className="metric-icon">{icon}</div>
      </div>
      <div className="metric-value">{value}</div>
      <div className="metric-bottom">
        <span className={`metric-change ${trend}`}>
          <ArrowUpRight size={14} /> {change}
        </span>
        <span>{note}</span>
      </div>
    </div>
  );
}

function ActivityItem({
  icon,
  title,
  detail,
  time,
  tone
}: {
  icon: React.ReactNode;
  title: string;
  detail: string;
  time: string;
  tone: string;
}) {
  return (
    <div className="activity-item">
      <div className={`activity-icon ${tone}`}>{icon}</div>
      <div className="activity-copy">
        <strong>{title}</strong>
        <span>{detail}</span>
      </div>
      <time>{time}</time>
    </div>
  );
}
