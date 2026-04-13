import { Metadata } from "next";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export const metadata: Metadata = {
  title: "Air Quality Delhi - Get Personalized Health Briefings | AirBrief",
  description: "Real-time air quality data for Delhi. Get personalized health briefings based on your health profile. Know when it's safe to exercise outdoors.",
};

const CITIES = [
  { name: "Delhi", slug: "delhi", lat: 28.7041, lon: 77.1025 },
  { name: "Mumbai", slug: "mumbai", lat: 19.076, lon: 72.8777 },
  { name: "Visakhapatnam", slug: "visakhapatnam", lat: 17.6868, lon: 83.2185 },
  { name: "Bangalore", slug: "bangalore", lat: 12.9716, lon: 77.5946 },
  { name: "Chennai", slug: "chennai", lat: 13.0827, lon: 80.2707 },
  { name: "Kolkata", slug: "kolkata", lat: 22.5726, lon: 88.3639 },
  { name: "Hyderabad", slug: "hyderabad", lat: 17.385, lon: 78.4867 },
  { name: "Beijing", slug: "beijing", lat: 39.9042, lon: 116.4074 },
  { name: "Jakarta", slug: "jakarta", lat: -6.2088, lon: 106.8456 },
];

export default function CityLandingPage({ params }: { params: { city: string } }) {
  const city = CITIES.find((c) => c.slug === params.city) || CITIES[0];
  
  const structuredData = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    "name": `Air Quality ${city.name} - AirBrief`,
    "description": `Real-time air quality data and health briefings for ${city.name}`,
    "about": {
      "@type": "Place",
      "name": city.name,
      "geo": {
        "@type": "GeoCoordinates",
        "latitude": city.lat,
        "longitude": city.lon
      }
    }
  };

  return (
    <div className="min-h-screen">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(structuredData) }}
      />
      
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between px-4">
          <Link href="/" className="text-xl font-bold">AirBrief</Link>
          <div className="flex gap-4">
            <Link href="/login"><Button variant="ghost">Login</Button></Link>
            <Link href="/register"><Button>Get Started</Button></Link>
          </div>
        </div>
      </header>

      <main className="container px-4 py-16">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Air Quality in {city.name}
          </h1>
          <p className="text-xl text-muted-foreground mb-8">
            Get personalized health briefings based on real-time air quality data.
            Know when it&apos;s safe to exercise, whether to wear a mask, and how today compares to your baseline.
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

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Real-Time Data</h3>
            <p className="text-muted-foreground">
              Live AQI readings from monitoring stations near {city.name}.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Health Briefings</h3>
            <p className="text-muted-foreground">
              AI-powered personalized advice calibrated to your health profile.
            </p>
          </div>
          <div className="p-6 border rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Daily Emails</h3>
            <p className="text-muted-foreground">
              Morning briefings delivered to your inbox every day.
            </p>
          </div>
        </div>
      </main>

      <footer className="border-t py-6 mt-16">
        <div className="container px-4 text-center text-sm text-muted-foreground">
          <p>AirBrief - Your personal air quality health advisor</p>
        </div>
      </footer>
    </div>
  );
}

export function generateStaticParams() {
  return CITIES.map((city) => ({ city: city.slug }));
}
