"use server";

const API_BASE = process.env.API_BASE_URL || "http://127.0.0.1:8000/api";

export interface UploadResponse {
  job_id: string;
  participants: string[];
  status: string;
  group_name: string | null;
}

export interface AnalyzeResponse {
  job_id: string;
  message: string;
  status: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  progress: number;
  current_step: string;
  created_at: string;
}

export interface StatsResponse {
  job_id: string;
  metadata: Record<string, unknown>;
  stats: Record<string, unknown>;
  status: string;
}

export type ActionResult<T> = { success: true; data: T } | { success: false; error: string };

export async function startAnalysis(
  jobId: string,
  selectedMembers: string[]
): Promise<AnalyzeResponse> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      job_id: jobId,
      selected_members: selectedMembers,
    }),
  });

  if (!response.ok) {
    throw new Error(`Analysis failed: ${response.statusText}`);
  }

  return response.json();
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to get job status: ${response.statusText}`);
  }

  return response.json();
}

export async function getJobStats(jobId: string): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE}/jobs/${jobId}/stats`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`Failed to get stats: ${response.statusText}`);
  }

  return response.json();
}
