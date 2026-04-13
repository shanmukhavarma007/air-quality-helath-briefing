"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Brush } from "recharts";

interface HistoricalTrendChartProps {
  data: { date: string; value: number }[];
  threshold?: number;
}

export function HistoricalTrendChart({ data, threshold = 100 }: HistoricalTrendChartProps) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="text-lg font-semibold mb-4">30-Day AQI Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            {threshold > 0 && (
              <Line
                type="monotone"
                dataKey="value"
                stroke="#ef4444"
                strokeDasharray="5 5"
                isAnimationActive={false}
              />
            )}
            <Line
              type="monotone"
              dataKey="value"
              stroke="#8884d8"
              strokeWidth={2}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      {threshold > 0 && (
        <div className="mt-4 flex items-center text-sm">
          <span className="w-3 h-3 rounded-full bg-red-500 mr-2" />
          <span className="text-muted-foreground">Unhealthy Threshold (AQI 100)</span>
        </div>
      )}
    </div>
  );
}