"use client";

import Link from "next/link";
import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  Bot,
  Building2,
  Eye,
  EyeOff,
  LockKeyhole,
  Mail,
  Sparkles,
} from "lucide-react";
import { register } from "@/lib/api";

function validatePassword(value: string): string {
  if (value.length < 8) {
    return "Password must contain at least 8 characters.";
  }

  if (!/[A-Za-z]/.test(value) || !/[0-9]/.test(value)) {
    return "Password must include at least one letter and one number.";
  }

  return "";
}

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();
    const passwordError = validatePassword(password);

    if (!trimmedName) {
      setError("Business name is required.");
      return;
    }

    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(trimmedEmail)) {
      setError("A valid email address is required.");
      return;
    }

    if (passwordError) {
      setError(passwordError);
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const result = await register(trimmedName, trimmedEmail, password);
      localStorage.setItem("msaidizi_token", result.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to create your account.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />

      <Link href="/" className="login-brand">
        <div className="brand-mark"><Sparkles size={21} /></div>
        <span>msaidizi<span className="brand-dot">.</span></span>
      </Link>

      <section className="glass-panel login-card">
        <div className="login-emblem"><Bot size={27} /></div>
        <div className="eyebrow"><span className="eyebrow-line" /> GET STARTED</div>
        <h1>Build a smarter<br />customer experience.</h1>
        <p className="login-description">
          Create your business account and start building your AI customer support assistant.
        </p>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit}>
          <label htmlFor="business-name">Business name</label>
          <div className="input-wrap">
            <Building2 size={17} />
            <input
              id="business-name"
              type="text"
              placeholder="e.g. Nairobi Threads"
              value={name}
              onChange={(event) => setName(event.target.value)}
              maxLength={120}
              required
            />
          </div>

          <label htmlFor="register-email">Business email</label>
          <div className="input-wrap">
            <Mail size={17} />
            <input
              id="register-email"
              type="email"
              placeholder="you@company.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </div>

          <label htmlFor="register-password">Password</label>
          <div className="input-wrap">
            <LockKeyhole size={17} />
            <input
              id="register-password"
              type={showPassword ? "text" : "password"}
              placeholder="At least 8 characters"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              maxLength={128}
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

          <label htmlFor="register-confirm-password">Confirm password</label>
          <div className="input-wrap">
            <LockKeyhole size={17} />
            <input
              id="register-confirm-password"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Re-enter your password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              minLength={8}
              maxLength={128}
              required
            />
            <button
              type="button"
              className="icon-button inline-toggle"
              onClick={() => setShowConfirmPassword((current) => !current)}
              aria-label={showConfirmPassword ? "Hide password" : "Show password"}
            >
              {showConfirmPassword ? <EyeOff size={17} /> : <Eye size={17} />}
            </button>
          </div>

          <button className="primary-button login-submit" type="submit" disabled={loading}>
            {loading ? "Creating account..." : <>Create business account <ArrowRight size={17} /></>}
          </button>
        </form>

        <div className="register-switch">
          Already have an account? <Link href="/login">Sign in</Link>
        </div>

        <div className="login-security">
          <LockKeyhole size={13} /> Your business workspace is private and secure.
        </div>
      </section>

      <div className="login-footer">
        © 2026 Msaidizi AI <span>·</span> Thoughtful support, powered by AI.
      </div>
    </main>
  );
}
