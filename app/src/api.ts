import type { CommandResult, Project, Settings } from "./types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options
  });
  let payload: unknown;
  try {
    payload = await response.json();
  } catch (error) {
    throw new Error(`Invalid JSON response: ${error instanceof Error ? error.message : String(error)}`);
  }
  if (!response.ok) {
    throw new Error(
      typeof payload === "object" && payload !== null && "message" in payload
        ? String((payload as Record<string, unknown>).message)
        : `Request failed with status ${response.status}`
    );
  }
  return payload as T;
}

export function getSettings() {
  return request<Settings>("/api/settings");
}

export function getProjects() {
  return request<Project[]>("/api/projects");
}

export function createProject(project: Partial<Project>) {
  return request<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(project)
  });
}

export function updateProject(id: string, patch: Partial<Project>) {
  return request<Project>(`/api/projects/${encodeURIComponent(id)}`, {
    method: "PATCH",
    body: JSON.stringify(patch)
  });
}

export function bootstrapProject(id: string) {
  return request<{ ok: boolean; message: string; result: CommandResult; project: Project }>(
    `/api/projects/${encodeURIComponent(id)}/bootstrap`,
    { method: "POST" }
  );
}

export function runProjectAction(id: string, action: string) {
  return request<{ ok: boolean; result: CommandResult; project: Project }>(
    `/api/projects/${encodeURIComponent(id)}/actions/${action}`,
    { method: "POST" }
  );
}

export function openSystemPath(target: string) {
  return request<{ ok: boolean; command: string; path: string }>("/api/system/open-path", {
    method: "POST",
    body: JSON.stringify({ target })
  });
}
