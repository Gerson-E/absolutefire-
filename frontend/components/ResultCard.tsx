/**
 * ResultCard — displays classification badge, reasoning, detection list,
 * and a reset button.
 *
 * Owner: Owner 1 — Frontend
 */

import type { AnalyzeResponse, USClass } from "@/lib/types";
import { DetectionOverlay } from "./DetectionOverlay";

const BADGE_STYLES: Record<USClass, string> = {
  "US-1": "bg-green-100 text-green-800 border-green-200",
  "US-2": "bg-yellow-100 text-yellow-800 border-yellow-200",
  "US-3": "bg-red-100 text-red-800 border-red-200",
};

const BADGE_LABELS: Record<USClass, string> = {
  "US-1": "US-1 — No suspicious observations",
  "US-2": "US-2 — Sub-threshold observation",
  "US-3": "US-3 — Positive",
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
  const cls = result.classification;
  const obs = result.largest_observation;

  return (
    <div className="space-y-6">
      {/* Classification badge */}
      <div
        className={`rounded-lg border p-4 text-center ${BADGE_STYLES[cls]}`}
      >
        <p className="text-2xl font-bold">{cls}</p>
        <p className="mt-1 text-sm">{BADGE_LABELS[cls]}</p>
      </div>

      {/* Image with detection overlay */}
      {result.detections.length > 0 && (
        <div className="overflow-hidden rounded-lg border border-gray-200 bg-black">
          <DetectionOverlay imageUrl={imageUrl} detections={result.detections} />
        </div>
      )}

      {/* Largest observation detail */}
      {obs.present && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            Largest Suspicious Observation
          </h3>
          <dl className="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm">
            <dt className="text-gray-500">Label</dt>
            <dd className="font-medium">{obs.label}</dd>
            <dt className="text-gray-500">Confidence</dt>
            <dd className="font-medium">
              {obs.confidence !== null
                ? `${(obs.confidence * 100).toFixed(1)}%`
                : "—"}
            </dd>
            <dt className="text-gray-500">Size (px)</dt>
            <dd className="font-medium">
              {obs.size_px !== null ? `${obs.size_px.toFixed(1)} px` : "—"}
            </dd>
            <dt className="text-gray-500">Size (mm)</dt>
            <dd className="font-medium">
              {obs.size_mm !== null ? `${obs.size_mm.toFixed(1)} mm` : "—"}
            </dd>
          </dl>
        </div>
      )}

      {/* Reasoning */}
      {result.reasoning.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700">Reasoning</h3>
          <ul className="mt-2 space-y-1">
            {result.reasoning.map((r, i) => (
              <li key={i} className="text-sm text-gray-600">
                &bull; {r}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {result.warnings.length > 0 && (
        <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4">
          <h3 className="text-sm font-semibold text-yellow-800">Warnings</h3>
          <ul className="mt-2 space-y-1">
            {result.warnings.map((w, i) => (
              <li key={i} className="text-sm text-yellow-700">
                &bull; {w}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* All detections table */}
      {result.detections.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="text-sm font-semibold text-gray-700">
            All Detections ({result.detections.length})
          </h3>
          <table className="mt-2 w-full text-left text-sm">
            <thead>
              <tr className="border-b text-xs text-gray-400">
                <th className="pb-1 font-medium">Label</th>
                <th className="pb-1 font-medium">Confidence</th>
                <th className="pb-1 font-medium">Bbox (x, y, w, h)</th>
              </tr>
            </thead>
            <tbody>
              {result.detections.map((d, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-1.5 font-medium">{d.label}</td>
                  <td className="py-1.5">
                    {(d.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="py-1.5 text-xs text-gray-500">
                    {d.bbox_xywh.map((v) => v.toFixed(1)).join(", ")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Reset */}
      <button
        onClick={onReset}
        className="w-full rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-semibold text-gray-700 shadow-sm transition hover:bg-gray-50"
      >
        Analyze Another Image
      </button>
    </div>
  );
}
