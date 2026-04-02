/**
 * UploadForm — image file picker + optional px_per_mm field + submit.
 *
 * Owner: Owner 1 — Frontend
 */

"use client";

import { useRef, useState } from "react";

const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE_MB = 20;

export function UploadForm({
  onSubmit,
}: {
  onSubmit: (file: File, pxPerMm?: number) => void;
}) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [pxPerMm, setPxPerMm] = useState("");
  const [error, setError] = useState<string | null>(null);

  function handleFile(e: React.ChangeEvent<HTMLInputElement>) {
    setError(null);
    const selected = e.target.files?.[0];
    if (!selected) return;

    if (!ACCEPTED_TYPES.includes(selected.type)) {
      setError("Unsupported file type. Please upload a JPEG, PNG, or WebP image.");
      return;
    }
    if (selected.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`File too large. Maximum size is ${MAX_SIZE_MB} MB.`);
      return;
    }

    setFile(selected);
    setPreview(URL.createObjectURL(selected));
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) return;

    const calibration = pxPerMm.trim() ? parseFloat(pxPerMm) : undefined;
    if (calibration !== undefined && (isNaN(calibration) || calibration <= 0)) {
      setError("Calibration must be a positive number.");
      return;
    }

    onSubmit(file, calibration);
  }

  function handleClear() {
    setFile(null);
    setPreview(null);
    setPxPerMm("");
    setError(null);
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Drop zone / file picker */}
      <div
        onClick={() => fileRef.current?.click()}
        className="cursor-pointer rounded-lg border-2 border-dashed border-gray-300 bg-white p-8 text-center transition hover:border-blue-400 hover:bg-blue-50/30"
      >
        {preview ? (
          <img
            src={preview}
            alt="Preview"
            className="mx-auto max-h-64 rounded object-contain"
          />
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">
              Click to select an ultrasound image
            </p>
            <p className="text-xs text-gray-400">
              JPEG, PNG, or WebP &mdash; max {MAX_SIZE_MB} MB
            </p>
          </div>
        )}
        <input
          ref={fileRef}
          type="file"
          accept=".jpg,.jpeg,.png,.webp"
          onChange={handleFile}
          className="hidden"
        />
      </div>

      {file && (
        <p className="text-center text-xs text-gray-500">
          {file.name}{" "}
          <button
            type="button"
            onClick={handleClear}
            className="text-blue-600 hover:underline"
          >
            Change
          </button>
        </p>
      )}

      {error && <p className="text-center text-sm text-red-600">{error}</p>}

      {/* Calibration field */}
      <div>
        <label
          htmlFor="px_per_mm"
          className="block text-sm font-medium text-gray-700"
        >
          Calibration factor{" "}
          <span className="font-normal text-gray-400">(optional)</span>
        </label>
        <div className="mt-1 flex items-center gap-2">
          <input
            id="px_per_mm"
            type="number"
            step="any"
            min="0"
            placeholder="e.g. 3.5"
            value={pxPerMm}
            onChange={(e) => setPxPerMm(e.target.value)}
            className="w-40 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
          <span className="text-xs text-gray-400">px / mm</span>
        </div>
        <p className="mt-1 text-xs text-gray-400">
          Without calibration, size cannot be measured in mm and the system will
          classify conservatively.
        </p>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={!file}
        className="w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Analyze Ultrasound
      </button>
    </form>
  );
}
