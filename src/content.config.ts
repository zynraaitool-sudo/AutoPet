import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const emptyToUndefined = (value: unknown) =>
  value == null || (typeof value === "string" && value.trim() === "") ? undefined : value;
const emptyToArray = (value: unknown) =>
  value == null || (typeof value === "string" && value.trim() === "") ? [] : value;

const reviews = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/reviews" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    updated: z.preprocess(emptyToUndefined, z.coerce.date().optional()),
    category: z.string(),
    image: z.preprocess(emptyToUndefined, z.string().optional()),
    imageAlt: z.preprocess(emptyToUndefined, z.string().optional()),
    draft: z.boolean().default(true),
    quickVerdict: z.preprocess(emptyToUndefined, z.string().default("")),
    products: z.preprocess(
      emptyToArray,
      z.array(
        z.object({
          name: z.string(),
          priceRange: z.string(),
          features: z.preprocess(emptyToArray, z.array(z.string()).default([])),
          rating: z.preprocess(
            emptyToUndefined,
            z.coerce.number().min(0).max(5).optional(),
          ),
          url: z.preprocess(emptyToUndefined, z.string().url().optional()),
          image: z.preprocess(emptyToUndefined, z.string().optional()),
        }),
      ),
    ),
    pros: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    cons: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    faqs: z.preprocess(
      emptyToArray,
      z.array(
        z.object({
          question: z.string(),
          answer: z.string(),
        }),
      ).default([]),
    ),
  }),
});

export const collections = { reviews };
