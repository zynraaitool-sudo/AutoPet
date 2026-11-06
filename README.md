# AutoPet

AutoPet is a static Astro site for practical smart-pet product reviews. It builds to `dist/` and is configured for Cloudflare Pages.

## Run locally

1. Install Node.js (the current Astro-supported LTS release).
2. In this folder, run `npm install`.
3. Run `npm run dev` and open the local address Astro prints.
4. Run `npm run build` to create the production site in `dist/`.

## Add an article

1. Create a Markdown file in `src/content/reviews/`, for example `quiet-pet-fountain.md`.
2. Add the required frontmatter: `title`, `description`, `date`, `category`, `draft`, `quickVerdict`, `products`, `pros`, `cons`, and `faqs`. `updated` is optional. See `best-automatic-cat-feeders-2026.md` for the expected shape.
3. Write the article body in Markdown. Product entries need `name`, `priceRange`, `features`, `rating` (0–5), and a valid `url`.
4. Set `draft: true` while working. Draft reviews are excluded from category pages, home, and article routes; change it to `false` when ready to publish.
5. Before publishing, replace affiliate placeholders listed in `TODO.md`, then run `npm run build`.

## Change the colors

Edit the CSS custom properties at the top of the global styles in `src/layouts/SiteLayout.astro`. The main palette is `--ink`, `--teal`, `--teal-deep`, `--sun`, `--sun-deep`, `--paper`, and `--mist`. Check text/background combinations for WCAG AA contrast after changing them.

## Deploy to Cloudflare Pages with GitHub

1. Push this project to a GitHub repository.
2. In Cloudflare, open **Workers & Pages → Create → Pages → Connect to Git** and select that repository.
3. Set the build command to `npm run build` and the build output directory to `dist`.
4. Leave the root directory as `/` and use the Node.js version supported by the current Astro release in the project settings.
5. Save and deploy. Cloudflare will build on later pushes to the connected branch.

The public domain is set to `https://autopet.store` in `astro.config.mjs`; update it there if the production domain changes.
