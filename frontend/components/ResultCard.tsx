/**
 * ResultCard — displays classification badge, reasoning, detection details,
 * and a reset button.
 *
 * Owner: Owner 1 — Frontend
 */

import type { AnalyzeResponse } from "@/lib/types";

const CLASS_STYLES: Record<string, string> = {
  "US-1": "bg-green-100 text-green-800 border-green-200",
  "US-2": "bg-yellow-100 text-yellow-800 border-yellow-200",
  "US-3": "bg-red-100 text-red-800 border-red-200",
};

export function ResultCard({
  result,
  imageUrl,
  onReset,
}: {
  result: AnalyzeResponse;
  imageUrl: string;
  onReset: () => void;
}) {
  const { classification, reasoning, largest_observation, warnings } = result;
  const badgeStyle = CLASS_STYLES[classification] ?? "bg-gray-100 text-gray-800";

  return (
    <div className="space-y-6">
      {/* Image preview */}
      <img
        src={imageUrl}
        alt="Uploaded ultrasound"
        className="w-full rounded-lg border border-gray-200 object-contain"
        style={{ maxHeight: 320 }}
      />

      {/* Classification badge */}
      <div className={`rounded-lg border px-5 py-4 ${badgeStyle}`}>
        <p className="text-xs font-medium uppercase tracking-wide opacity-70">
          LI-RADS Classification
        </p>
        <p className="mt-1 text-3xl font-bold">{classification}</p>
      </div>

      {/* Largest observation */}
      {largest_observation.present && (
        <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm">
          <p className="font-medium text-gray-700">Largest HCC Detection</p>
          <ul className="mt-2 space-y-1 text-gray-600">
            <li>Confidence: {((largest_observation.confidence ?? 0) * 100).toFixed(1)}%</li>
            <li>Size: {largest_observation.size_px} px
              {largest_observation.size_mm !== null
                ? ` (${largest_observation.size_mm} mm)`
                : " (mm unavailable — no calibration)"}
            </li>
          </ul>
        </div>
      )}

      {/* Reasoning */}
      <div>
        <p className="mb-2 text-sm font-medium text-gray-700">Reasoning</p>
        <ul className="space-y-1">
          {reasoning.map((r, i) => (
            <li key={i} className="text-sm text-gray-600">
              — {r}
            </li>
          ))}
        </ul>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 px-4 py-3">
          {warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-800">{w}</p>
          ))}
        </div>
      )}

      <button
        onClick={onReset}
        className="w-full rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        Analyze another image
      </button>
    </div>
  );
}
