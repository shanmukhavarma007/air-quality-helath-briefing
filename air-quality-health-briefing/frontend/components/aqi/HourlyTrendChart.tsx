"use client";

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface HourlyTrendChartProps {
  data: { time: string; value: number }[];
  bestWindow?: string;
  worstWindow?: string;
}

export function HourlyTrendChart({ data, bestWindow, worstWindow }: HourlyTrendChartProps) {
  return (
    <div className="rounded-lg border bg-card p-6">
      <h3 className="text-lg font-semibold mb-4">Hourly AQI Trend</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis dataKey="time" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
            />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.3}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 flex gap-4 text-sm">
        {bestWindow && (
          <div className="flex items-center">
            <span className="w-3 h-3 rounded-full bg-green-500 mr-2" />
            <span className="text-muted-foreground">Best: </span>
            <span className="font-medium">{bestWindow}</span>
          </div>
        )}
        {worstWindow && (
          <div className="flex items-center">
            <span className="w-3 h-3 rounded-full bg-red-500 mr-2" />
            <span className="text-muted-foreground">Worst: </span>
            <span className="font-medium">{worstWindow}</span>
          </div>
        )}
      </div>
    </div>
  );
}
