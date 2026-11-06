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
    draft: z.boolean().default(false),
    quickVerdict: z.string(),
    products: z.array(
      z.object({
        name: z.string(),
        priceRange: z.string(),
        features: z.array(z.string()),
        rating: z.number().min(0).max(5),
        url: z.string().url(),
        image: z.string().optional(),
      }),
    ),
    pros: z.array(z.string()),
    cons: z.array(z.string()),
    faqs: z.array(
      z.object({
        question: z.string(),
        answer: z.string(),
      }),
    ),
  }),
});

export const collections = { reviews };
