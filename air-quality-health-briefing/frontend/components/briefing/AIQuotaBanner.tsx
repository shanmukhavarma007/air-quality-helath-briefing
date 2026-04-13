"use client";

import { QuotaStatus } from "@/types";
import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";

interface AIQuotaBannerProps {
  quota: QuotaStatus;
}

export function AIQuotaBanner({ quota }: AIQuotaBannerProps) {
  if (quota.remaining >= 10) {
    return null;
  }

  const isCritical = quota.remaining === 0;

  return (
    <div
      className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-lg",
        isCritical ? "bg-red-100 text-red-800" : "bg-amber-100 text-amber-800"
      )}
    >
      <AlertTriangle className="h-5 w-5" />
      <div className="flex-1">
        <span className="font-medium">
          {isCritical
            ? "AI quota exhausted"
            : `${quota.remaining} AI briefings remaining today`}
        </span>
        <span className="text-sm ml-2 opacity-80">
          Resets at {quota.resets_at}
        </span>
      </div>
    </div>
  );
}
