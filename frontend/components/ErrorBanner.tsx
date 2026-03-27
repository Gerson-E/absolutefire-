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
    <div className="flex items-start justify-between rounded-lg border border-red-200 bg-red-50 px-4 py-3">
      <p className="text-sm text-red-700">{message}</p>
      <button
        onClick={onDismiss}
        className="ml-4 text-red-400 hover:text-red-600"
        aria-label="Dismiss error"
      >
        ✕
      </button>
    </div>
  );
}
