# AutoPet

AutoPet is a static Astro site for practical smart-pet product reviews. It builds to `dist/` and is configured for Cloudflare Pages.

## Run locally

1. Install Node.js (the current Astro-supported LTS release).
2. In this folder, run `npm install`.
3. Run `npm run dev` and open the local address Astro prints.
4. Run `npm run build` to create the production site in `dist/`.

## Manage products and articles

Products and editorial articles are separate content collections with separate draft flags and publishing lifecycles:

- **Products** are Markdown files in `src/content/products/`. A published product has a public detail page at `/products/<slug>/` when `draft: false`. Set `catalogVisible: false` to keep that page and its URL while excluding the item from the curated catalog and homepage. Product categories include feeders, fountains, grooming, dog walking/travel, and interactive cat toys.
- **Reviews & Guides** remain Markdown files in `src/content/reviews/`. Their existing `/reviews/<slug>/` URLs are unchanged; published articles appear in `/reviews/` and on the homepage only when `draft: false`.

New CMS entries default to drafts. Save a draft to keep it private; when it is ready, uncheck its own **Draft — keep unpublished** field to publish it. Product and article drafts do not publish one another. The sitemap is generated from public routes, so drafts are excluded.

Products support direct `productUrl` links and optional tracked `affiliateUrl` links; when both are present, the affiliate URL is used. Affiliate disclosures appear only for tracked links. Images are optional; add only materials you have permission to publish. Product copy identifies seller claims and does not imply hands-on testing unless testing was actually performed. Product pages may include an ordered image gallery, HTTP(S) YouTube/MP4 video links, specifications, features, pros and cons, optional price, and an optional link to a published article. Host large video files externally; do not commit them to Git.

The Decap CMS has separate **Products** and **Reviews & Guides** sections. Product images are stored in a folder named for each product, so uploading an image with the same filename for another product will not replace it. Sign in at `/admin/` as described in [Publish with Decap CMS](#publish-with-decap-cms).

## Add an article

1. Create a Markdown file in `src/content/reviews/`, for example `quiet-pet-fountain.md`.
2. Add the required frontmatter: `title`, `description`, `date`, `category`, and `draft`. `updated`, featured image fields, quick verdict, products, pros, cons, and FAQs are optional. See `automatic-cat-feeder-listings-and-buying-guide.md` for an example.
3. Write the article body in Markdown. Comparison entries need `name` and `priceRange`; `features`, `rating` (0–5), `ratingNote`, `image`, and a valid retailer `url` are optional. Set `affiliate: false` on a direct retailer URL; tracked links default to affiliate.
4. Set `draft: true` while working. Draft reviews are excluded from category pages, home, the editorial listing, and article routes; change it to `false` when ready to publish.
5. Before publishing, replace affiliate placeholders listed in `TODO.md`, then run `npm run build`.

The Decap editor also provides raw HTML, affiliate button, callout, and quick comparison table blocks from the Markdown editor's **+** menu. Raw HTML blocks are rendered as HTML; use them only for trusted content.

## Change the colors

Edit the CSS custom properties at the top of the global styles in `src/layouts/SiteLayout.astro`. The main palette is `--ink`, `--teal`, `--teal-deep`, `--sun`, `--sun-deep`, `--paper`, and `--mist`. Check text/background combinations for WCAG AA contrast after changing them.

## Deploy to Cloudflare Pages with GitHub

1. Push this project to a GitHub repository.
2. In Cloudflare, open **Workers & Pages → Create → Pages → Connect to Git** and select that repository.
3. Set the build command to `npm run build` and the build output directory to `dist`.
4. Leave the root directory as `/` and use the Node.js version supported by the current Astro release in the project settings.
5. Save and deploy. Cloudflare will build on later pushes to the connected branch.

The public domain is set to `https://autopet.store` in `astro.config.mjs`; update it there if the production domain changes.

## Publish with Decap CMS

1. Create a GitHub OAuth App with homepage URL `https://autopet.store` and authorization callback URL `https://autopet.store/api/callback`.
2. In the Cloudflare Pages project, add `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` as environment variables for production. Use the OAuth App's Client ID and Client secret, then redeploy.
3. Visit `https://autopet.store/admin/` and sign in with a GitHub account that can push to `zynraaitool-sudo/AutoPet`.
4. Create or edit a product under **Products** or an article under **Reviews & Guides**. New entries start as drafts. Decap saves product files in `src/content/products` and articles in `src/content/reviews`.
5. To publish an entry, uncheck its **Draft — keep unpublished** field and save. This changes only that entry's publishing status and triggers a Pages build.

The editor fields follow `src/content.config.ts`. `catalogVisible` controls whether a published product appears in recommendations; it does not change the product page or draft state. Existing article publication statuses are preserved, and renamed article URLs have redirects. Product gallery order follows the order of its CMS image list. Use externally hosted HTTPS MP4 files instead of adding large videos to the repository.
