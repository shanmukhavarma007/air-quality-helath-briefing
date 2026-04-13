"use client";

import { useEffect, useState } from "react";
import { Bell, AlertTriangle } from "lucide-react";
import { useRouter } from "next/navigation";
import { AQIData } from "@/types";
import { toast } from "sonner";

interface AlertBellProps {
  aqiData: AQIData | null;
}

export function AlertBell({ aqiData }: AlertBellProps) {
  const [alertCount, setAlertCount] = useState(0);
  const router = useRouter();

  useEffect(() => {
    if (aqiData) {
      checkAlertThreshold(aqiData);
    }
  }, [aqiData]);

  const checkAlertThreshold = (data: AQIData) => {
    // Check if we should show an alert based on AQI thresholds
    // For now, we'll use a default threshold of 150 (Unhealthy)
    // In a real app, this would come from user's location settings
    const threshold = 150;
    
    if (data.aqi_value >= threshold) {
      // Show toast notification
      toast.warning(`Air quality is ${data.category} (AQI: ${data.aqi_value}). Consider limiting outdoor activities.`, {
        duration: 10000,
        action: {
          label: "View Details",
          onClick: () => {
            router.push("/dashboard");
          }
        }
      });
      
      // Increment alert count (in a real app, this would come from backend)
      setAlertCount(prev => prev + 1);
    }
  };

  return (
    <div className="relative">
      <button
        className="p-2 rounded hover:bg-muted"
        onClick={() => router.push("/dashboard")}
      >
        {alertCount > 0 ? (
          <AlertTriangle className="h-5 w-5 text-red-500 animate-pulse" />
        ) : (
          <Bell className="h-5 w-5 text-muted-foreground hover:text-primary" />
        )}
        {alertCount > 0 && (
          <span className="absolute -top-1 -right-1 flex h-3 w-3 items-center justify-center text-xs font-medium rounded-full bg-red-500 text-white">
            {alertCount}
          </span>
        )}
      </div>
    );
}