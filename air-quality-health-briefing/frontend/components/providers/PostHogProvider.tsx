'use client'

import { useEffect } from 'react'
import { usePathname, useSearchParams } from 'next/navigation'
import { useSession } from 'next-auth/react'
import { initPostHog, posthog } from '@/lib/posthog'
import { analytics } from '@/lib/analytics'

export function PostHogProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const searchParams = useSearchParams()
  const { data: session, status } = useSession()

  useEffect(() => {
    initPostHog()
  }, [])

  // Identify users on login
  useEffect(() => {
    if (status === 'authenticated' && session?.user) {
      posthog.identify(session.user.id, {
        email: session.user.email,
        has_conditions: session.user.healthProfile?.conditions?.length > 0,
        age_bracket: session.user.healthProfile?.age_bracket,
        activity_level: session.user.healthProfile?.activity_level,
      })
    } else if (status === 'unauthenticated') {
      posthog.reset()  // Clear identity on logout
    }
  }, [session, status])

  // Manually capture page views on route change (required for App Router)
  useEffect(() => {
    if (pathname) {
      let url = window.origin + pathname
      if (searchParams?.toString()) url += `?${searchParams.toString()}`
      posthog.capture('$pageview', { '$current_url': url })
    }
  }, [pathname, searchParams])

  return <>{children}</>
}
