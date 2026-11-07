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
  markdown: {
    processor: unified({
      remarkPlugins: [remarkHtmlBlocks],
      rehypePlugins: [rehypeAffiliateLinks],
    }),
  },
  integrations: [
    sitemap({
      filter: (page) => !new URL(page).pathname.startsWith("/admin"),
    }),
  ],
});
