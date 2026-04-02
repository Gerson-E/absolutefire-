"use client";

/**
 * Home page — entry point for the upload + result flow.
 *
 * Owner: Owner 1 — Frontend
 */

import { useState } from "react";
import type { AnalyzeResponse } from "@/lib/types";
import { analyzeUltrasound } from "@/lib/api";
import { UploadForm } from "@/components/UploadForm";
import { ResultCard } from "@/components/ResultCard";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ErrorBanner } from "@/components/ErrorBanner";

type State =
  | { step: "idle" }
  | { step: "loading"; imageUrl: string }
  | { step: "result"; result: AnalyzeResponse; imageUrl: string }
  | { step: "error"; message: string };

export default function HomePage() {
  const [state, setState] = useState<State>({ step: "idle" });

  async function handleSubmit(file: File, pxPerMm?: number) {
    const imageUrl = URL.createObjectURL(file);
    setState({ step: "loading", imageUrl });

    try {
      const result = await analyzeUltrasound(file, pxPerMm);
      setState({ step: "result", result, imageUrl });
    } catch (err) {
      URL.revokeObjectURL(imageUrl);
      const message =
        err instanceof Error ? err.message : "An unexpected error occurred.";
      setState({ step: "error", message });
    }
  }

  function handleReset() {
    if (state.step === "result") {
      URL.revokeObjectURL(state.imageUrl);
    }
    setState({ step: "idle" });
  }

  return (
    <div className="space-y-8">
      {state.step === "error" && (
        <ErrorBanner
          message={state.message}
          onDismiss={() => setState({ step: "idle" })}
        />
      )}

      {state.step === "idle" && <UploadForm onSubmit={handleSubmit} />}

      {state.step === "loading" && <LoadingSpinner />}

      {state.step === "result" && (
        <ResultCard
          result={state.result}
          imageUrl={state.imageUrl}
          onReset={handleReset}
        />
      )}
    </div>
  );
}
