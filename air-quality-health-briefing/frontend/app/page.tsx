import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between px-4">
          <span className="text-xl font-bold">AirBrief</span>
          <div className="flex gap-4">
            <Link href="/login">
              <Button variant="ghost">Login</Button>
            </Link>
            <Link href="/register">
              <Button>Sign Up</Button>
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center">
        <div className="container px-4 py-16">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Know What&apos;s in the Air You Breathe
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Get personalized health briefings based on real-time air quality data,
              weather context, and your health profile.
            </p>
            <div className="flex gap-4 justify-center">
              <Link href="/register">
                <Button size="lg">Get Started</Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg">Login</Button>
              </Link>
            </div>
          </div>
        </div>
      </main>

      <footer className="border-t py-6">
        <div className="container px-4 text-center text-sm text-muted-foreground">
          <p>Air Quality Health Briefing - AI-powered air quality insights</p>
        </div>
      </footer>
    </div>
  );
}
