"use client";

import { useState } from "react";
import { analyzeUltrasound, ApiError } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";
import { UploadForm } from "@/components/UploadForm";
import { ResultCard } from "@/components/ResultCard";
import { LoadingSpinner } from "@/components/LoadingSpinner";
import { ErrorBanner } from "@/components/ErrorBanner";

type State =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "result"; data: AnalyzeResponse; imageUrl: string }
  | { status: "error"; message: string };

export default function HomePage() {
  const [state, setState] = useState<State>({ status: "idle" });

  async function handleSubmit(file: File, pxPerMm?: number) {
    setState({ status: "loading" });
    const imageUrl = URL.createObjectURL(file);
    try {
      const data = await analyzeUltrasound(file, pxPerMm);
      setState({ status: "result", data, imageUrl });
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Unexpected error — please try again.";
      setState({ status: "error", message });
    }
  }

  function reset() {
    setState({ status: "idle" });
  }

  return (
    <div className="space-y-6">
      {state.status === "error" && (
        <ErrorBanner message={state.message} onDismiss={reset} />
      )}

      {state.status === "idle" && <UploadForm onSubmit={handleSubmit} />}

      {state.status === "loading" && <LoadingSpinner />}

      {state.status === "result" && (
        <ResultCard
          result={state.data}
          imageUrl={state.imageUrl}
          onReset={reset}
        />
      )}
    </div>
  );
}
