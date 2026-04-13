"use client";

import { Briefing } from "@/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface HealthBriefCardProps {
  briefing: Briefing;
  isLoading?: boolean;
}

export function HealthBriefCard({ briefing, isLoading }: HealthBriefCardProps) {
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Health Brief</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-3/4" />
            <div className="h-4 bg-muted rounded w-1/2" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const safetyColors = {
    safe: "bg-green-100 text-green-800",
    caution: "bg-yellow-100 text-yellow-800",
    avoid: "bg-red-100 text-red-800",
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Health Brief</span>
          {briefing.is_cached_result && (
            <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
              Cached
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-2">
          <span
            className={cn(
              "px-3 py-1 rounded-full text-sm font-medium",
              safetyColors[briefing.outdoor_safety as keyof typeof safetyColors] || "bg-gray-100"
            )}
          >
            {briefing.outdoor_safety?.toUpperCase() || "UNKNOWN"} for outdoor activity
          </span>
        </div>

        <p className="text-lg">{briefing.summary}</p>

        {briefing.best_time_window && (
          <div className="p-3 bg-muted rounded-lg">
            <span className="font-medium">Best Time: </span>
            {briefing.best_time_window}
          </div>
        )}

        {briefing.mask_recommendation && (
          <div className="p-3 bg-muted rounded-lg">
            <span className="font-medium">Mask Recommendation: </span>
            {briefing.mask_recommendation}
          </div>
        )}

        {briefing.symptom_watch && briefing.symptom_watch.length > 0 && (
          <div>
            <span className="font-medium">Symptoms to Watch: </span>
            <div className="flex flex-wrap gap-2 mt-2">
              {briefing.symptom_watch.map((symptom, i) => (
                <span key={i} className="px-2 py-1 bg-muted rounded text-sm">
                  {symptom}
                </span>
              ))}
            </div>
          </div>
        )}

        <p className="text-sm text-muted-foreground">{briefing.activity_guidance}</p>

        {briefing.historical_context && (
          <p className="text-sm text-muted-foreground italic">
            {briefing.historical_context}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
