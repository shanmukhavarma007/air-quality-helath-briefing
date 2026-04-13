"use client";

import { AQIData } from "@/types";
import { cn } from "@/lib/utils";

interface AQIGaugeProps {
  data: AQIData;
  isLoading?: boolean;
}

export function AQIGauge({ data, isLoading }: AQIGaugeProps) {
  if (isLoading) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg bg-muted animate-pulse">
        <span className="text-muted-foreground">Loading AQI...</span>
      </div>
    );
  }

  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg p-6 text-white"
      style={{ backgroundColor: data.hex_color }}
    >
      <div className="text-6xl font-bold">{data.aqi_value}</div>
      <div className="mt-2 text-xl font-medium">{data.category}</div>
      <div className="mt-4 text-sm">
        <span className="opacity-80">📍 {data.station_name}</span>
        {data.station_distance && (
          <span className="ml-2 opacity-80">
            ({data.station_distance.toFixed(1)} km away)
          </span>
        )}
      </div>
      <div className="mt-2 text-xs opacity-70">
        Updated: {new Date(data.last_updated).toLocaleTimeString()}
      </div>
    </div>
  );
}
