"use client";

import { ArrowRight, Bot, Eye, EyeOff, LockKeyhole, Mail, Sparkles } from "lucide-react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmedEmail = email.trim();
    setLoading(true);
    setError("");

    if (!trimmedEmail || !password) {
      setError("Email and password are required.");
      setLoading(false);
      return;
    }

    try {
      const result = await login(trimmedEmail, password);
      localStorage.setItem("msaidizi_token", result.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <div className="login-brand">
        <div className="brand-mark"><Sparkles size={21} /></div>
        <span>msaidizi<span className="brand-dot">.</span></span>
      </div>

      <section className="glass-panel login-card">
        <div className="login-emblem"><Bot size={27} /></div>
        <div className="eyebrow"><span className="eyebrow-line" /> WELCOME BACK</div>
        <h1>Your business,<br />in good hands.</h1>
        <p className="login-description">
          Sign in to your workspace and let your AI assistant take care of the conversations.
        </p>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email address</label>
          <div className="input-wrap">
            <Mail size={17} />
            <input
              id="email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <label htmlFor="password">Password</label>
          <div className="input-wrap">
            <LockKeyhole size={17} />
            <input
              id="password"
              type={showPassword ? "text" : "password"}
              placeholder="Enter your password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button
              type="button"
              className="icon-button inline-toggle"
              onClick={() => setShowPassword((current) => !current)}
              aria-label={showPassword ? "Hide password" : "Show password"}
            >
              {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>

          <button className="primary-button login-submit" type="submit" disabled={loading}>
            {loading ? "Signing in..." : <>Sign in to workspace <ArrowRight size={17} /></>}
          </button>
        </form>

        <div className="register-switch">
          Need an account? <Link href="/register">Create business account</Link>
        </div>

        <div className="login-security"><LockKeyhole size={13} /> Your workspace is private and secure.</div>
      </section>

      <div className="login-footer">© 2026 Msaidizi AI <span>·</span> Thoughtful support, powered by AI.</div>
    </main>
  );
}
