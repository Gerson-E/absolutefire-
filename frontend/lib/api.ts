/**
 * Backend API client.
 *
 * Owner: Owner 1 — Frontend
 *
 * This is the only file in frontend/ that knows the backend URL.
 * All API communication goes through here.
 */

import type { AnalyzeResponse } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Submit a liver ultrasound image for LI-RADS classification.
 *
 * @param file      The image file selected by the user.
 * @param pxPerMm   Optional physical calibration factor (pixels per mm).
 *                  When provided, size_mm will be populated in the response.
 */
export async function analyzeUltrasound(
  file: File,
  pxPerMm?: number,
): Promise<AnalyzeResponse> {
  const form = new FormData();
  form.append("image", file);
  if (pxPerMm !== undefined) {
    form.append("px_per_mm", String(pxPerMm));
  }

  const response = await fetch(`${API_BASE}/api/analyze-ultrasound`, {
    method: "POST",
    body: form,
  });

  if (!response.ok) {
    let message = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail ?? message;
    } catch {
      // ignore parse failures
    }
    throw new ApiError(response.status, message);
  }

  return response.json() as Promise<AnalyzeResponse>;
}
