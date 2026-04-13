"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Navbar } from "@/components/layout/Navbar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import api from "@/lib/api";
import { toast } from "sonner";
import { UserLocation } from "@/types";

export default function SettingsPage() {
  const router = useRouter();
  const [locations, setLocations] = useState<UserLocation[]>([]);
  const [newLocation, setNewLocation] = useState({ label: "", latitude: "", longitude: "" });
  const [isLoading, setIsLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);

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

  const addLocation = async () => {
    if (!newLocation.label || !newLocation.latitude || !newLocation.longitude) {
      toast.error("Please fill all fields");
      return;
    }
    setIsAdding(true);
    try {
      await api.post("/locations", {
        label: newLocation.label,
        latitude: parseFloat(newLocation.latitude),
        longitude: parseFloat(newLocation.longitude),
      });
      toast.success("Location added!");
      setNewLocation({ label: "", latitude: "", longitude: "" });
      await loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to add location");
    } finally {
      setIsAdding(false);
    }
  };

  const deleteLocation = async (id: string) => {
    try {
      await api.delete(`/locations/${id}`);
      toast.success("Location deleted!");
      await loadLocations();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Failed to delete location");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Settings</h1>
        
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Manage Locations</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {locations.map((loc) => (
                  <div key={loc.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <span className="font-medium">{loc.label}</span>
                      <span className="text-sm text-muted-foreground ml-2">
                        ({loc.latitude}, {loc.longitude})
                      </span>
                      {loc.is_primary && (
                        <span className="ml-2 text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                          Primary
                        </span>
                      )}
                    </div>
                    <Button variant="destructive" size="sm" onClick={() => deleteLocation(loc.id)}>
                      Delete
                    </Button>
                  </div>
                ))}
                
                <div className="pt-4 border-t">
                  <h3 className="font-medium mb-4">Add New Location</h3>
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <Label>Label</Label>
                      <Input
                        placeholder="Home, Office..."
                        value={newLocation.label}
                        onChange={(e) => setNewLocation({ ...newLocation, label: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label>Latitude</Label>
                      <Input
                        placeholder="17.6868"
                        value={newLocation.latitude}
                        onChange={(e) => setNewLocation({ ...newLocation, latitude: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label>Longitude</Label>
                      <Input
                        placeholder="83.2185"
                        value={newLocation.longitude}
                        onChange={(e) => setNewLocation({ ...newLocation, longitude: e.target.value })}
                      />
                    </div>
                    <div className="flex items-end">
                      <Button onClick={addLocation} disabled={isAdding}>
                        {isAdding ? "Adding..." : "Add Location"}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
