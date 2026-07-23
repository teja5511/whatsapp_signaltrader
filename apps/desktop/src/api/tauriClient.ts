// Safe Tauri Rust Proxy Bridge with Browser Fallback

let memoryToken: string | null = null;

export const isTauriAvailable = (): boolean => {
  return typeof window !== "undefined" && ("__TAURI_INTERNALS__" in window || "__TAURI__" in window);
};

export async function secureTokenSet(token: string): Promise<void> {
  memoryToken = token.trim();
  if (isTauriAvailable()) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("secure_token_set", { token: memoryToken });
    } catch {
      // In-memory fallback
    }
  }
}

export async function secureTokenExists(): Promise<boolean> {
  if (isTauriAvailable()) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke<boolean>("secure_token_exists");
    } catch {
      return Boolean(memoryToken);
    }
  }
  return Boolean(memoryToken);
}

export async function secureTokenClear(): Promise<void> {
  memoryToken = null;
  if (isTauriAvailable()) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      await invoke("secure_token_clear");
    } catch {
      // Clear fallback
    }
  }
}

export interface TauriApiResponse {
  status: number;
  body: string;
  ok: boolean;
}

export async function secureApiRequest(
  url: string,
  method: string = "GET",
  body?: any,
  headers?: Record<string, string>
): Promise<TauriApiResponse> {
  const isLoopback = url.startsWith("http://127.0.0.1") || url.startsWith("http://localhost");
  if (!isLoopback && !url.startsWith("https://")) {
    throw new Error("Security Error: Non-loopback plain HTTP requests are blocked.");
  }

  if (isTauriAvailable()) {
    try {
      const { invoke } = await import("@tauri-apps/api/core");
      return await invoke<TauriApiResponse>("secure_api_request", {
        url,
        method,
        body: body ? JSON.stringify(body) : null,
        headers: headers || null,
      });
    } catch (e: any) {
      // Fall through to browser fetch proxy if Tauri invoke fails in test/dev
    }
  }

  // Browser fetch fallback for dev & tests
  const requestHeaders: Record<string, string> = { ...headers };
  if (body) {
    requestHeaders["Content-Type"] = "application/json";
  }
  if (memoryToken) {
    requestHeaders["Authorization"] = `Bearer ${memoryToken}`;
  }

  const res = await fetch(url, {
    method,
    headers: requestHeaders,
    body: body ? JSON.stringify(body) : undefined,
  });

  const responseText = await res.text();
  return {
    status: res.status,
    body: responseText,
    ok: res.ok,
  };
}
