import { z } from "zod";

export const registerSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z
    .string()
    .min(8, "At least 8 characters")
    .regex(/[A-Z]/, "Must contain an uppercase letter")
    .regex(/[0-9]/, "Must contain a number")
    .regex(/[!@#$%^&*(),.?":{}|<>]/, "Must contain a special character"),
  full_name: z
    .string()
    .min(2, "Name must be at least 2 characters")
    .max(100, "Name must be less than 100 characters"),
});

export const loginSchema = z.object({
  email: z.string().email("Enter a valid email address"),
  password: z.string().min(1, "Password is required"),
});

export const locationSchema = z.object({
  label: z.string().min(1, "Label is required").max(100),
  latitude: z.number().min(-90).max(90),
  longitude: z.number().min(-180).max(180),
  address: z.string().optional(),
  is_primary: z.boolean().default(false),
  alert_threshold: z.number().min(0).max(500).default(150),
});

export const healthProfileSchema = z.object({
  age_bracket: z.enum(["child", "adult", "senior"]).default("adult"),
  conditions: z.array(z.string()).default([]),
  activity_level: z.enum(["sedentary", "moderate", "athlete"]).default("moderate"),
  briefing_time: z.string().default("07:00"),
  timezone: z.string().default("UTC"),
});
