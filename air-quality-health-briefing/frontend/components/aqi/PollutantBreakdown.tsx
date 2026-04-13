"use client";

import { AQIData } from "@/types";

interface PollutantBreakdownProps {
  data: AQIData;
}

export function PollutantBreakdown({ data }: PollutantBreakdownProps) {
  const pollutants = [
    { name: "PM2.5", value: data.pm25, unit: "µg/m³" },
    { name: "PM10", value: data.pm10, unit: "µg/m³" },
    { name: "O₃", value: data.o3, unit: "µg/m³" },
    { name: "NO₂", value: data.no2, unit: "µg/m³" },
    { name: "CO", value: data.co, unit: "mg/m³" },
    { name: "SO₂", value: data.so2, unit: "µg/m³" },
  ].filter((p) => p.value !== undefined && p.value !== null);

  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="text-lg font-semibold mb-4">Pollutant Breakdown</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {pollutants.map((pollutant) => (
          <div key={pollutant.name} className="flex flex-col">
            <span className="text-sm text-muted-foreground">{pollutant.name}</span>
            <span className="text-xl font-semibold">
              {pollutant.value ?? "N/A"}
              <span className="text-xs font-normal ml-1">{pollutant.unit}</span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
