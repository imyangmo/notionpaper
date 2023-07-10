import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import node from '@astrojs/node';
import sitemap from '@astrojs/sitemap';

import image from "@astrojs/image";
import partytown from '@astrojs/partytown';

// https://astro.build/config
export default defineConfig({
  site: 'https://notionpaper.cc',
  // integrations: [mdx(), sitemap()] 
  integrations: [mdx(), sitemap(), image(), partytown({
    // Example: Disable debug mode.
    config: { debug: false },
  })]
  // output: 'server',
  // adapter: node(),

});