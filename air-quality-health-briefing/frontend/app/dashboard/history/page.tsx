"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from "@/lib/api";
import { Briefing } from "@/types";

export default function HistoryPage() {
  const router = useRouter();
  const [briefings, setBriefings] = useState<Briefing[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadHistory();
  }, [router]);

  const loadHistory = async () => {
    try {
      const response = await api.get("/briefings/history", { params: { limit: 30 } });
      setBriefings(response.data);
    } catch (error: any) {
      console.error("Failed to load history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Briefing History</h1>
        {isLoading ? (
          <div className="animate-pulse">Loading...</div>
        ) : (
          <div className="space-y-4">
            {briefings.map((briefing) => (
              <Card key={briefing.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>{new Date(briefing.generated_at).toLocaleDateString()}</span>
                    {briefing.is_cached_result && (
                      <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded">
                        Cached
                      </span>
                    )}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-lg">{briefing.summary}</p>
                  <div className="mt-2 text-sm text-muted-foreground">
                    AQI: {briefing.aqi_at_generation} | Safety: {briefing.outdoor_safety}
                  </div>
                </CardContent>
              </Card>
            ))}
            {briefings.length === 0 && (
              <p className="text-muted-foreground">No briefings yet.</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
