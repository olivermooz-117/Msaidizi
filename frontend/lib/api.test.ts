import assert from "node:assert/strict";
import test from "node:test";

import { buildApiUrl, toErrorMessage } from "./api.ts";

test("buildApiUrl appends the configured backend URL", () => {
  assert.equal(buildApiUrl("/api/auth/login"), "http://127.0.0.1:5000/api/auth/login");
});

test("buildApiUrl strips trailing slashes from the API base", () => {
  process.env.NEXT_PUBLIC_API_URL = "http://localhost:5000/";
  assert.equal(buildApiUrl("/api/auth/login"), "http://localhost:5000/api/auth/login");
});

test("toErrorMessage surfaces API error payloads", () => {
  assert.equal(toErrorMessage({ error: "Invalid email or password." }, "fallback"), "Invalid email or password.");
  assert.equal(toErrorMessage({ message: "Server error" }, "fallback"), "Server error");
  assert.equal(toErrorMessage("custom error", "fallback"), "custom error");
  assert.equal(toErrorMessage({}, "fallback"), "fallback");
});
