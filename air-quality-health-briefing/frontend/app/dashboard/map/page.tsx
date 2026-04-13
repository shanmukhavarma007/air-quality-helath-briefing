"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import api from "@/lib/api";
import { UserLocation } from "@/types";

export default function MapPage() {
  const router = useRouter();
  const [locations, setLocations] = useState<UserLocation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.push("/login");
      return;
    }
    loadLocations();
  }, [router]);

  const loadLocations = async () => {
    try {
      const response = await api.get("/locations");
      setLocations(response.data);
    } catch (error: any) {
      console.error("Failed to load locations:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Location Map</h1>
        {isLoading ? (
          <div className="animate-pulse">Loading...</div>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle>Your Saved Locations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4">
                {locations.map((loc) => (
                  <div key={loc.id} className="p-4 border rounded-lg">
                    <div className="font-medium">{loc.label}</div>
                    <div className="text-sm text-muted-foreground">
                      Lat: {loc.latitude}, Lon: {loc.longitude}
                    </div>
                    {loc.address && (
                      <div className="text-sm text-muted-foreground">{loc.address}</div>
                    )}
                  </div>
                ))}
                {locations.length === 0 && (
                  <p className="text-muted-foreground">
                    No locations saved yet. Add locations in Settings.
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
