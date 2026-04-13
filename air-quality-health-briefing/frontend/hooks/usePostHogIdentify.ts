'use client'

import { useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { posthog } from '@/lib/posthog'

export function usePostHogIdentify() {
  const { data: session, status } = useSession()

  useEffect(() => {
    if (status === 'authenticated' && session?.user) {
      posthog.identify(session.user.id, {
        email: session.user.email,
        // Send health profile dimensions for cohort analysis
        // Do NOT send raw condition names if you want to avoid HIPAA-adjacent data
        has_conditions: session.user.healthProfile?.conditions?.length > 0,
        age_bracket: session.user.healthProfile?.age_bracket,
        activity_level: session.user.healthProfile?.activity_level,
      })
    } else if (status === 'unauthenticated') {
      posthog.reset()  // Clear identity on logout
    }
  }, [session, status])
}