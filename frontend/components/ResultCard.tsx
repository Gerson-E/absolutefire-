/**
 * ResultCard — displays classification badge, reasoning, detection list,
 * and a reset button.
 *
 * Owner: Owner 1 — Frontend
 *
 * Props:
 *   result: AnalyzeResponse
 *   imageUrl: string         (object URL of the uploaded image)
 *   onReset: () => void
 *
 * TODO: implement
 */

import type { AnalyzeResponse } from "@/lib/types";

export function ResultCard(_props: {
  result: AnalyzeResponse;
  imageUrl: string;
  onReset: () => void;
}) {
  return <div>TODO: ResultCard</div>;
}
