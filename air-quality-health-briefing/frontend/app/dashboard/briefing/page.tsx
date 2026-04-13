"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { HealthBriefCard } from "@/components/briefing/HealthBriefCard";
import { AIQuotaBanner } from "@/components/briefing/AIQuotaBanner";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import api from "@/lib/api";
import { Briefing, QuotaStatus } from "@/types";

export default function BriefingPage() {
  const router = useRouter();
  const [briefing, setBriefing] = useState<Briefing | null>(null);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);

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
      const [briefingRes, quotaRes] = await Promise.all([
        api.get("/briefings/history", { params: { limit: 1 } }),
        api.get("/briefings/quota"),
      ]);
      if (briefingRes.data.length > 0) {
        setBriefing(briefingRes.data[0]);
      }
      setQuota(quotaRes.data);
    } catch (error: any) {
      console.error("Failed to load briefing:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const generateNewBriefing = async () => {
    setIsGenerating(true);
    try {
      const response = await api.post("/briefings/generate", {});
      setBriefing(response.data);
      const quotaRes = await api.get("/briefings/quota");
      setQuota(quotaRes.data);
      toast.success("Briefing generated!");
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to generate briefing");
    } finally {
      setIsGenerating(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navbar />
        <main className="container px-4 py-8 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Health Briefing</h1>
          <Button onClick={generateNewBriefing} disabled={isGenerating}>
            {isGenerating ? "Generating..." : "Generate New Briefing"}
          </Button>
        </div>

        {quota && <AIQuotaBanner quota={quota} />}

        <div className="mt-6">
          {briefing ? (
            <HealthBriefCard briefing={briefing} />
          ) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">
                No briefing available yet. Generate your first briefing to get personalized health recommendations.
              </p>
              <Button onClick={generateNewBriefing} disabled={isGenerating}>
                Generate Your First Briefing
              </Button>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
