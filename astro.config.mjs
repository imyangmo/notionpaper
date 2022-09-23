import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import node from '@astrojs/node';
import sitemap from '@astrojs/sitemap';

import image from "@astrojs/image";

// https://astro.build/config
export default defineConfig({
  site: 'https://notionpaper.cc',
  // integrations: [mdx(), sitemap()] 
  integrations: [mdx(), sitemap(), image()] 
  // output: 'server',
  // adapter: node(),

});