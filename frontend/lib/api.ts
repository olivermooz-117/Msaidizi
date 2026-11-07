const DEFAULT_API_URL = "http://127.0.0.1:5000";

export function getApiBase(): string {
  return (process.env.NEXT_PUBLIC_API_URL || DEFAULT_API_URL).replace(/\/$/, "");
}

export const API_URL = getApiBase();

export type DocumentItem = {
  id: string;
  title: string;
  source_type?: string;
  created_at?: string;
};

export type AuthResponse = {
  access_token: string;
  business?: {
    id: string;
    name: string;
    email: string;
  };
};

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${getApiBase()}${normalizedPath}`;
}

export function toErrorMessage(data: unknown, fallback: string): string {
  if (typeof data === "string" && data.trim()) return data;

  if (data && typeof data === "object") {
    const value = data as Record<string, unknown>;
    if (typeof value.error === "string" && value.error.trim()) return value.error;
    if (typeof value.message === "string" && value.message.trim()) return value.message;
  }

  return fallback;
}

async function readJsonSafely(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";

  if (!contentType.includes("application/json")) {
    return {};
  }

  try {
    return await response.json();
  } catch {
    return {};
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string
): Promise<T> {
  const url = buildApiUrl(path);
  const headers = new Headers(options.headers || {});

  if (
    options.body !== undefined &&
    options.body !== null &&
    !(options.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
      cache: "no-store",
    });

    const data = await readJsonSafely(response);

    if (!response.ok) {
      const status = response.status;
      if (status === 401) {
        throw new Error(toErrorMessage(data, "Invalid email or password."));
      }

      if (status === 409) {
        throw new Error(toErrorMessage(data, "Email address is already registered."));
      }

      if (status === 400) {
        throw new Error(toErrorMessage(data, "Please check the form and try again."));
      }

      if (status >= 500) {
        throw new Error(toErrorMessage(data, "Server error. Please try again later."));
      }

      throw new Error(toErrorMessage(data, `Request failed (${status})`));
    }

    return data as T;
  } catch (error) {
    if (error instanceof TypeError) {
      throw new Error("Unable to connect to the server. Please try again later.");
    }

    if (error instanceof Error) {
      throw error;
    }

    throw new Error("Request failed. Please try again later.");
  }
}

export async function login(email: string, password: string) {
  return request<AuthResponse>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(
  name: string,
  email: string,
  password: string
) {
  return request<AuthResponse>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

export async function getDocuments(token: string) {
  const result = await request<DocumentItem[] | { documents?: DocumentItem[] }>(
    "/api/knowledge/documents",
    {},
    token
  );

  return Array.isArray(result) ? result : result.documents || [];
}

export async function addDocument(
  token: string,
  title: string,
  content: string
) {
  return request(
    "/api/knowledge/documents",
    {
      method: "POST",
      body: JSON.stringify({
        title,
        content,
        source_type: "paste",
      }),
    },
    token
  );
}
