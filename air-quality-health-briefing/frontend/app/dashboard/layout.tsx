'use client'

import { usePostHogIdentify } from '@/hooks/usePostHogIdentify'

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  usePostHogIdentify()
  return <>{children}</>
}