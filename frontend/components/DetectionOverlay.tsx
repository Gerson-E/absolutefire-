/**
 * DetectionOverlay — renders bounding boxes over the uploaded image.
 *
 * Owner: Owner 1 — Frontend
 */

"use client";

import { useEffect, useRef, useState } from "react";
import type { Detection } from "@/lib/types";

export function DetectionOverlay({
  imageUrl,
  detections,
}: {
  imageUrl: string;
  detections: Detection[];
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [naturalSize, setNaturalSize] = useState<{
    w: number;
    h: number;
  } | null>(null);

  useEffect(() => {
    const img = new Image();
    img.onload = () => setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
    img.src = imageUrl;
  }, [imageUrl]);

  return (
    <div ref={containerRef} className="relative inline-block w-full">
      <img
        src={imageUrl}
        alt="Uploaded ultrasound"
        className="w-full rounded"
        onLoad={(e) => {
          const img = e.currentTarget;
          setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
        }}
      />

      {naturalSize &&
        detections.map((det, i) => {
          const [cx, cy, w, h] = det.bbox_xywh;
          // Convert from center-based coords to top-left percentages
          const left = ((cx - w / 2) / naturalSize.w) * 100;
          const top = ((cy - h / 2) / naturalSize.h) * 100;
          const width = (w / naturalSize.w) * 100;
          const height = (h / naturalSize.h) * 100;

          return (
            <div
              key={i}
              className="absolute border-2 border-red-500"
              style={{
                left: `${left}%`,
                top: `${top}%`,
                width: `${width}%`,
                height: `${height}%`,
              }}
            >
              <span className="absolute -top-5 left-0 whitespace-nowrap rounded bg-red-500 px-1 py-0.5 text-[10px] font-medium text-white">
                {det.label} {(det.confidence * 100).toFixed(0)}%
              </span>
            </div>
          );
        })}
    </div>
  );
}
