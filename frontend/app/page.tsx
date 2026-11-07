import Link from "next/link";
import {
  ArrowRight,
  ArrowUpRight,
  Bot,
  BrainCircuit,
  Check,
  ChevronRight,
  Globe2,
  MessageCircle,
  ShieldCheck,
  Sparkles,
  Zap,
  BookOpen,
  Clock3,
  Menu
} from "lucide-react";

const features = [
  {
    icon: MessageCircle,
    number: "01",
    title: "Conversations that feel human",
    description:
      "Give customers helpful, natural answers without making them wait for someone to become available."
  },
  {
    icon: BrainCircuit,
    number: "02",
    title: "AI that knows your business",
    description:
      "Teach your assistant using your own FAQs, product details, services and business policies."
  },
  {
    icon: Clock3,
    number: "03",
    title: "Always ready to help",
    description:
      "Give your customers a place to find answers even when your team is busy or your doors are closed."
  }
];

const benefits = [
  "Spend less time answering repetitive questions",
  "Give customers faster and more consistent responses",
  "Keep your business information in one place",
  "Stay focused on running and growing your business"
];

export default function HomePage() {
  return (
    <main className="marketing-shell">
      <div className="marketing-orb orb-one" />
      <div className="marketing-orb orb-two" />
      <div className="marketing-orb orb-three" />

      <header className="marketing-nav">
        <Link href="/" className="marketing-brand">
          <span className="marketing-brand-icon">
            <Sparkles size={21} />
          </span>
          <span>msaidizi<span className="brand-dot">.</span></span>
        </Link>

        <nav className="marketing-links">
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#about">About</a>
        </nav>

        <div className="marketing-actions">
          <Link href="/login" className="nav-login">Login</Link>
          <Link href="/register" className="nav-register">
            Get started <ArrowUpRight size={15} />
          </Link>
        </div>

        <Link href="/login" className="mobile-nav-login" aria-label="Login">
          <Menu size={22} />
        </Link>
      </header>

      <section className="marketing-hero">
        <div className="hero-copy">
          <div className="marketing-eyebrow">
            <span className="eyebrow-pulse" />
            BUILT FOR BUSINESSES THAT THINK AHEAD
          </div>

          <h1>
            Better conversations.
            <br />
            <span>Smarter business.</span>
          </h1>

          <p className="marketing-lead">
            Meet your new AI customer support assistant. Msaidizi helps
            businesses answer questions, support customers and create
            better experiences — without the busywork.
          </p>

          <div className="hero-actions">
            <Link href="/register" className="hero-primary">
              Create your account <ArrowRight size={18} />
            </Link>
            <a href="#features" className="hero-secondary">
              Discover Msaidizi <ChevronRight size={17} />
            </a>
          </div>

          <div className="hero-trust">
            <div className="trust-icon"><ShieldCheck size={17} /></div>
            <span>Built with your business and customers in mind.</span>
          </div>
        </div>

        <div className="hero-visual">
          <div className="visual-orbit orbit-a" />
          <div className="visual-orbit orbit-b" />

          <div className="assistant-window glass-panel">
            <div className="assistant-window-top">
              <div className="window-dots">
                <i /><i /><i />
              </div>
              <span>MSAIDIZI AI EXPERIENCE</span>
              <span className="window-live"><span /> LIVE</span>
            </div>

            <div className="assistant-profile">
              <div className="assistant-avatar"><Bot size={27} /></div>
              <div>
                <strong>Your AI assistant</strong>
                <span><i /> Ready to help your customers</span>
              </div>
              <div className="assistant-sparkle"><Sparkles size={19} /></div>
            </div>

            <div className="chat-date">A BETTER CUSTOMER EXPERIENCE STARTS HERE</div>

            <div className="chat-message assistant-message">
              Hello! 👋 Welcome to our business. How can I help you today?
            </div>

            <div className="chat-message customer-message">
              Hi! I'd like to know more about your products.
            </div>

            <div className="chat-message assistant-message">
              Absolutely! I'd be happy to help. I can tell you about our
              products, pricing and delivery options.
            </div>

            <div className="chat-input-preview">
              <span>Ask me anything...</span>
              <div><ArrowRight size={16} /></div>
            </div>

            <div className="assistant-footnote">
              <Sparkles size={12} /> Powered by Msaidizi AI
            </div>
          </div>

          <div className="floating-stat stat-top">
            <div className="floating-stat-icon purple"><Zap size={17} /></div>
            <div><strong>Always ready</strong><span>Customer support</span></div>
          </div>

          <div className="floating-stat stat-bottom">
            <div className="floating-stat-icon green"><Check size={17} /></div>
            <div><strong>Business-aware AI</strong><span>Knowledge-powered answers</span></div>
          </div>
        </div>
      </section>

      <section className="marketing-strip">
        <span>MADE FOR THE WAY MODERN BUSINESSES WORK</span>
        <div><Globe2 size={16} /> Local businesses. Bigger possibilities.</div>
        <div><ShieldCheck size={16} /> Your business, your knowledge.</div>
        <div><Zap size={16} /> Less busywork, more growth.</div>
      </section>

      <section className="marketing-section" id="features">
        <div className="section-intro">
          <div className="marketing-eyebrow">A SMARTER WAY TO SUPPORT</div>
          <h2>
            Your customers deserve
            <br />
            <span>more than an auto-reply.</span>
          </h2>
          <p>
            Msaidizi brings your business knowledge and AI-powered support
            together, making it easier to deliver helpful customer experiences.
          </p>
        </div>

        <div className="feature-grid">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <article className="feature-card glass-panel" key={feature.number}>
                <div className="feature-card-top">
                  <div className="feature-icon"><Icon size={22} /></div>
                  <span>{feature.number}</span>
                </div>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <a href="#how-it-works" className="feature-link">
                  Explore <ArrowUpRight size={15} />
                </a>
              </article>
            );
          })}
        </div>
      </section>

      <section className="workflow-section" id="how-it-works">
        <div className="workflow-copy">
          <div className="marketing-eyebrow">SIMPLE BY DESIGN</div>
          <h2>
            Your knowledge.
            <br />
            <span>Your AI assistant.</span>
          </h2>
          <p>
            Getting started should be simple. Give Msaidizi the information
            that makes your business unique, and let it help answer customer
            questions.
          </p>

          <div className="workflow-benefits">
            {benefits.map((benefit) => (
              <div key={benefit}>
                <span><Check size={14} /></span>
                {benefit}
              </div>
            ))}
          </div>

          <Link href="/register" className="hero-primary">
            Start building your assistant <ArrowRight size={17} />
          </Link>
        </div>

        <div className="workflow-visual glass-panel">
          <div className="workflow-visual-heading">
            <div>
              <span className="section-kicker">YOUR BUSINESS KNOWLEDGE</span>
              <h3>Everything your AI needs.</h3>
            </div>
            <div className="knowledge-icon"><BookOpen size={21} /></div>
          </div>

          <div className="knowledge-example">
            <div className="knowledge-file"><BookOpen size={18} /></div>
            <div><strong>Frequently asked questions</strong><span>Common customer questions</span></div>
            <span className="file-check"><Check size={15} /></span>
          </div>
          <div className="knowledge-example">
            <div className="knowledge-file blue"><Globe2 size={18} /></div>
            <div><strong>Products and services</strong><span>Your business offering</span></div>
            <span className="file-check"><Check size={15} /></span>
          </div>
          <div className="knowledge-example">
            <div className="knowledge-file pink"><ShieldCheck size={18} /></div>
            <div><strong>Business policies</strong><span>Delivery, returns and more</span></div>
            <span className="file-check"><Check size={15} /></span>
          </div>

          <div className="knowledge-ai">
            <div className="knowledge-ai-icon"><Bot size={20} /></div>
            <div><strong>One helpful assistant.</strong><span>Ready to put your business knowledge to work.</span></div>
            <Sparkles size={19} />
          </div>
        </div>
      </section>

      <section className="marketing-cta" id="about">
        <div className="cta-glow" />
        <div className="cta-content">
          <div className="marketing-eyebrow">THE NEXT CONVERSATION STARTS WITH YOU</div>
          <h2>Make every customer<br /><span>feel looked after.</span></h2>
          <p>
            Give your business a smarter way to support customers.
            Start building with Msaidizi today.
          </p>
          <Link href="/register" className="cta-button">
            Get started with Msaidizi <ArrowRight size={18} />
          </Link>
          <span className="cta-note">Your business journey starts here.</span>
        </div>
        <div className="cta-art"><BrainCircuit size={130} strokeWidth={0.8} /></div>
      </section>

      <footer className="marketing-footer">
        <Link href="/" className="marketing-brand">
          <span className="marketing-brand-icon"><Sparkles size={19} /></span>
          <span>msaidizi<span className="brand-dot">.</span></span>
        </Link>
        <p>Thoughtful support, powered by AI.</p>
        <div className="footer-links">
          <Link href="/login">Login</Link>
          <Link href="/register">Register</Link>
          <a href="#features">Features</a>
        </div>
        <span className="copyright">© 2026 Msaidizi AI. All rights reserved.</span>
      </footer>
    </main>
  );
}
