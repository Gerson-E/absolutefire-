/**
 * UploadForm — image file picker + optional px_per_mm field + submit.
 *
 * Owner: Owner 1 — Frontend
 */

"use client";

import { useRef, useState } from "react";

export function UploadForm({
  onSubmit,
}: {
  onSubmit: (file: File, pxPerMm?: number) => void;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [pxPerMm, setPxPerMm] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;
    const calibration = pxPerMm ? parseFloat(pxPerMm) : undefined;
    onSubmit(file, calibration);
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div
        className="flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-white px-6 py-12 hover:border-blue-400"
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
        {file ? (
          <p className="text-sm font-medium text-gray-700">{file.name}</p>
        ) : (
          <>
            <p className="text-sm text-gray-500">Click to select an ultrasound image</p>
            <p className="mt-1 text-xs text-gray-400">JPEG, PNG, or WEBP — max 20 MB</p>
          </>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Calibration (px / mm) — optional
        </label>
        <input
          type="number"
          min="0.01"
          step="any"
          placeholder="e.g. 3.5"
          value={pxPerMm}
          onChange={(e) => setPxPerMm(e.target.value)}
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <p className="mt-1 text-xs text-gray-400">
          Without this, any HCC detection defaults to US-3 (conservative).
        </p>
      </div>

      <button
        type="submit"
        disabled={!file}
        className="w-full rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Analyze
      </button>
    </form>
  );
}
