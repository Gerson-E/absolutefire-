/**
 * ErrorBanner — displays an error message with a dismiss action.
 *
 * Owner: Owner 1 — Frontend
 */

export function ErrorBanner({
  message,
  onDismiss,
}: {
  message: string;
  onDismiss: () => void;
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2">
          <span className="mt-0.5 text-red-500">&#x2716;</span>
          <p className="text-sm text-red-700">{message}</p>
        </div>
        <button
          onClick={onDismiss}
          className="shrink-0 text-sm font-medium text-red-600 hover:text-red-800"
        >
          Dismiss
        </button>
      </div>
    </div>
  );
}
