import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";
import { isHttpUrl, isSafeMp4Url, youtubeVideoId } from "./lib/media";

const emptyToUndefined = (value: unknown) =>
  value == null || (typeof value === "string" && value.trim() === "") ? undefined : value;
const emptyToArray = (value: unknown) =>
  value == null || (typeof value === "string" && value.trim() === "") ? [] : value;

const safeHttpUrl = z.string().url().refine(isHttpUrl, "Must be an HTTP or HTTPS URL");

const reviews = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/reviews" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    updated: z.preprocess(emptyToUndefined, z.coerce.date().optional()),
    category: z.string(),
    articleType: z.enum(["product-review", "buying-guide", "comparison", "pet-care-guide"]).optional(),
    image: z.preprocess(emptyToUndefined, z.string().optional()),
    imageAlt: z.preprocess(emptyToUndefined, z.string().optional()),
    draft: z.boolean().default(true),
    quickVerdict: z.preprocess(emptyToUndefined, z.string().default("")),
    comparisonTitle: z.preprocess(emptyToUndefined, z.string().default("At a glance")),
    productLabel: z.preprocess(emptyToUndefined, z.string().default("Product")),
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
          ratingNote: z.preprocess(emptyToUndefined, z.string().optional()),
          url: z.preprocess(emptyToUndefined, z.string().url().optional()),
          image: z.preprocess(emptyToUndefined, z.string().optional()),
          affiliate: z.boolean().default(true),
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

const products = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/products" }),
  schema: z.object({
    name: z.string().min(1),
    category: z.enum([
      "automatic-cat-feeders",
      "pet-water-fountains",
      "smart-litter-boxes",
      "pet-inspired-toys",
      "pet-grooming",
      "dog-walking-travel",
      "interactive-cat-toys",
    ]),
    description: z.string().min(1),
    image: z.preprocess(emptyToUndefined, z.string().optional()),
    imageAlt: z.preprocess(emptyToUndefined, z.string().optional()),
    gallery: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    youtubeUrl: z.preprocess(
      emptyToUndefined,
      safeHttpUrl.refine((value) => youtubeVideoId(value) !== undefined, "Must be a valid YouTube video URL").optional(),
    ),
    videoUrl: z.preprocess(
      emptyToUndefined,
      safeHttpUrl.refine(isSafeMp4Url, "Must be an HTTP or HTTPS URL ending in .mp4").optional(),
    ),
    videoPoster: z.preprocess(emptyToUndefined, z.string().optional()),
    videoTitle: z.preprocess(emptyToUndefined, z.string().optional()),
    specifications: z.preprocess(
      emptyToArray,
      z.array(z.object({ name: z.string(), value: z.string() })).default([]),
    ),
    features: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    pros: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    cons: z.preprocess(emptyToArray, z.array(z.string()).default([])),
    price: z.preprocess(emptyToUndefined, z.string().optional()),
    productUrl: z.preprocess(emptyToUndefined, safeHttpUrl.optional()),
    affiliateUrl: z.preprocess(emptyToUndefined, safeHttpUrl.optional()),
    relatedArticle: z.preprocess(emptyToUndefined, z.string().optional()),
    catalogVisible: z.boolean().default(true),
    displayOrder: z.coerce.number().int().default(100),
    draft: z.boolean().default(true),
  }).refine((product) => Boolean(product.productUrl || product.affiliateUrl), {
    message: "Add a product URL or an affiliate URL",
    path: ["productUrl"],
  }),
});

export const collections = { reviews, products };
