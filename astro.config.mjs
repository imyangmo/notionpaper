import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import partytown from '@astrojs/partytown';

import vercel from "@astrojs/vercel/static";

// https://astro.build/config
export default defineConfig({
  site: 'https://notionpaper.cc',
  // integrations: [mdx(), sitemap()] 
  integrations: [mdx(), sitemap(), partytown({
    // Example: Disable debug mode.
    config: {
      debug: false
    }
  })]
  // output: 'server',
  // adapter: node(),
  ,
  output: "static",
  adapter: vercel({
    analytics: true,
  })
});