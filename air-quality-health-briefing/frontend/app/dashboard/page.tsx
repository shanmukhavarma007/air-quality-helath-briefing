"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { AQIGauge } from "@/components/aqi/AQIGauge";
import { PollutantBreakdown } from "@/components/aqi/PollutantBreakdown";
import { HourlyTrendChart } from "@/components/aqi/HourlyTrendChart";
import { HealthBriefCard } from "@/components/briefing/HealthBriefCard";
import { AIQuotaBanner } from "@/components/briefing/AIQuotaBanner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import { AQIData, Briefing, QuotaStatus, UserLocation } from "@/types";

export default function DashboardPage() {
  const router = useRouter();
  const [aqiData, setAqiData] = useState<AQIData | null>(null);
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [locations, setLocations] = useState<UserLocation[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<UserLocation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingBriefing, setIsGeneratingBriefing] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadData();
  }, [router]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [locationsRes, quotaRes] = await Promise.all([
        api.get("/locations"),
        api.get("/briefings/quota"),
      ]);
      setLocations(locationsRes.data);
      setQuota(quotaRes.data);
      
      if (locationsRes.data.length > 0) {
        const primary = locationsRes.data.find((l: UserLocation) => l.is_primary) || locationsRes.data[0];
        setSelectedLocation(primary);
        await loadAQI(primary.latitude, primary.longitude);
      }
    } catch (error: any) {
      if (error.response?.status === 401) {
        router.push("/login");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const loadAQI = async (lat: number, lon: number) => {
    try {
      const [aqiRes, briefingRes] = await Promise.all([
        api.get("/aqi/current", { params: { lat, lon } }),
        api.get("/briefings/history", { params: { limit: 1 } }),
      ]);
      setAqiData(aqiRes.data);
      if (briefingRes.data.length > 0) {
        setBriefing(briefingRes.data[0]);
      }
    } catch (error: any) {
      console.error("Failed to load AQI:", error);
    }
  };

  const handleLocationChange = async (location: UserLocation) => {
    setSelectedLocation(location);
    await loadAQI(location.latitude, location.longitude);
  };

  const generateBriefing = async () => {
    setIsGeneratingBriefing(true);
    try {
      const response = await api.post("/briefings/generate", {
        location_id: selectedLocation?.id,
      });
      setBriefing(response.data);
      const quotaRes = await api.get("/briefings/quota");
      setQuota(quotaRes.data);
      toast.success("Briefing generated!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to generate briefing");
    } finally {
      setIsGeneratingBriefing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container px-4 py-8">
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <h1 className="text-2xl font-bold flex-1">Air Quality Dashboard</h1>
          <select
            className="px-3 py-2 border rounded-md"
            value={selectedLocation?.id}
            onChange={(e) => {
              const loc = locations.find((l) => l.id === e.target.value);
              if (loc) handleLocationChange(loc);
            }}
          >
            {locations.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.label}
              </option>
            ))}
          </select>
        </div>

        {quota && <AIQuotaBanner quota={quota} />}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {aqiData && <AQIGauge data={aqiData} />}
          {briefing ? (
            <HealthBriefCard briefing={briefing} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Health Brief</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Generate your personalized health briefing based on current air quality.
                </p>
                <Button onClick={generateBriefing} disabled={isGeneratingBriefing}>
                  {isGeneratingBriefing ? "Generating..." : "Generate Briefing"}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {aqiData && <PollutantBreakdown data={aqiData} />}

        <div className="mt-6">
          <HourlyTrendChart
            data={Array.from({ length: 24 }, (_, i) => ({
              time: `${i}:00`,
              value: Math.floor(Math.random() * 100 + aqiData.aqi_value - 50),
            }))}
          />
        </div>
      </main>
    </div>
  );
}
