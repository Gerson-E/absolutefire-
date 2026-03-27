import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "US LI-RADS Classifier",
  description:
    "Prototype liver ultrasound surveillance classification — not for clinical use",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        <header className="border-b border-gray-200 bg-white px-6 py-4">
          <div className="mx-auto flex max-w-3xl items-center justify-between">
            <h1 className="text-lg font-semibold tracking-tight">
              US LI-RADS Classifier
            </h1>
            <span className="rounded-full bg-yellow-100 px-3 py-1 text-xs font-medium text-yellow-800">
              Prototype — Not for clinical use
            </span>
          </div>
        </header>
        <main className="mx-auto max-w-3xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
