import { defineConfig } from "astro/config";
import { unified } from "@astrojs/markdown-remark";
import sitemap from "@astrojs/sitemap";

const remarkHtmlBlocks = () => (tree) => {
  const transform = (node) => {
    if (node.type === "code" && node.lang === "html_block") {
      return {
        type: "html",
        value: `<div class="raw-html">\n${node.value}\n</div>`,
        position: node.position,
      };
    }

    if (node.children) {
      node.children = node.children.map(transform);
    }

    return node;
  };

  tree.children = tree.children.map(transform);
};

const rehypeAffiliateLinks = () => (tree) => {
  const visit = (node) => {
    if (node.type === "element" && node.tagName === "a") {
      const href = node.properties?.href;
      if (typeof href === "string" && /affiliate|REPLACE-WITH-AFFILIATE-LINK/i.test(href)) {
        node.properties.rel = ["sponsored", "nofollow", "noopener"];
      }
    }

    node.children?.forEach(visit);
  };

  visit(tree);
};

export default defineConfig({
  site: "https://autopet.store",
  redirects: {
    "/reviews/best-automatic-cat-feeders-in-2026-top-smart-wifi-budget-picks/":
      "/reviews/automatic-cat-feeder-listings-and-buying-guide/",
    "/reviews/independent-research-honest-comparisons-practical-recommendations/":
      "/reviews/automatic-cat-feeder-buying-guide/",
  },
  markdown: {
    processor: unified({
      remarkPlugins: [remarkHtmlBlocks],
      rehypePlugins: [rehypeAffiliateLinks],
    }),
  },
  integrations: [
    sitemap({
      filter: (page) => {
        const pathname = new URL(page).pathname;
        return pathname !== "/admin" &&
          !pathname.startsWith("/admin/") &&
          pathname !== "/404.html";
      },
    }),
  ],
});
