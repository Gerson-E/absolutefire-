/**
 * TypeScript types for the US LI-RADS API.
 *
 * Owner: Owner 1 — Frontend
 *
 * These types mirror shared/api-contract.md exactly.
 * Do not change field names without updating the contract.
 */

export type USClass = "US-1" | "US-2" | "US-3";

export interface LargestObservation {
  present: boolean;
  label: string | null;
  confidence: number | null;
  size_px: number | null;
  size_mm: number | null;
}

export interface Detection {
  label: string;
  confidence: number;
  /** [x_center, y_center, width, height] in pixels */
  bbox_xywh: [number, number, number, number];
}

export interface AnalyzeResponse {
  result_id: string;
  classification: USClass;
  reasoning: string[];
  largest_observation: LargestObservation;
  detections: Detection[];
  annotated_image_url: string | null;
  warnings: string[];
}

export interface AnalyzeError {
  detail: string;
}
