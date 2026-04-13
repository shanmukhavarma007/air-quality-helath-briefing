import { posthog } from './posthog'

export const analytics = {
  briefingGenerated(props: { aqi_value: number; aqi_category: string; city: string }) {
    posthog.capture('Briefing Generated', props)
  },

  briefingShared(props: { method: 'copy_link' | 'email' | 'whatsapp' }) {
    posthog.capture('Briefing Shared', props)
  },

  alertCreated(props: { threshold: number; pollutant: string }) {
    posthog.capture('Alert Created', props)
  },

  emailSubscribed(props: { frequency: 'daily' | 'twice_daily' }) {
    posthog.capture('Email Subscribed', props)
  },

  aiQuotaExhausted() {
    posthog.capture('AI Quota Exhausted')
  },

  fallbackBriefingShown(props: { aqi_value: number }) {
    posthog.capture('Fallback Briefing Shown', props)
  },

  locationAdded(props: { city: string; is_first_location: boolean }) {
    posthog.capture('Location Added', props)
  },

  onboardingCompleted(props: { has_conditions: boolean; activity_level: string }) {
    posthog.capture('Onboarding Completed', props)
  },
}