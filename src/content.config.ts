import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const reviews = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/reviews" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    updated: z.coerce.date().optional(),
    category: z.string(),
    image: z.string().optional(),
    imageAlt: z.string().optional(),
    draft: z.boolean().default(true),
    quickVerdict: z.string().default(""),
    products: z.array(
      z.object({
        name: z.string(),
        priceRange: z.string(),
        features: z.array(z.string()),
        rating: z.number().min(0).max(5),
        url: z.string().url(),
        image: z.string().optional(),
      }),
    ).default([]),
    pros: z.array(z.string()).default([]),
    cons: z.array(z.string()).default([]),
    faqs: z.array(
      z.object({
        question: z.string(),
        answer: z.string(),
      }),
    ).default([]),
  }),
});

export const collections = { reviews };
