"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Bell, Menu, User } from "lucide-react";
import { cn } from "@/lib/utils";
import { AlertBell } from "@/components/layout/AlertBell";

interface NavbarProps {
  aqiData: AQIData | null;
}

export function Navbar({ aqiData }: NavbarProps) {
  const pathname = usePathname();

  return (
    <nav className="border-b bg-background">
      <div className="container flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-8">
          <Link href="/" className="text-xl font-bold">
            AirBrief
          </Link>
          <div className="hidden md:flex items-center gap-6">
            <Link
              href="/dashboard"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname === "/dashboard" && "text-primary"
              )}
            >
              Dashboard
            </Link>
            <Link
              href="/dashboard/history"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname === "/dashboard/history" && "text-primary"
              )}
            >
              History
            </Link>
            <Link
              href="/dashboard/map"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname === "/dashboard/map" && "text-primary"
              )}
            >
              Map
            </Link>
            <Link
              href="/dashboard/settings"
              className={cn(
                "text-sm font-medium transition-colors hover:text-primary",
                pathname === "/dashboard/settings" && "text-primary"
              )}
            >
              Settings
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon">
            <AlertBell aqiData={aqiData} />
          </Button>
          <Button variant="ghost" size="icon">
            <User className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </nav>
  );
}
