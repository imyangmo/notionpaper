import { defineConfig } from 'astro/config';
import { loadEnv } from "vite";
const {
	RUNTIME
} = loadEnv(process.env.NODE_ENV, process.cwd(), "");
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import image from "@astrojs/image";
import partytown from '@astrojs/partytown';
import node from '@astrojs/node';
import vercelServerless from "@astrojs/vercel/serverless";
import vercelStatic from "@astrojs/vercel/static";
import netlify from "@astrojs/netlify/functions";

const errMsg = '[NOTIONPAPER] ENV variable "RUNTIME" error, accepted: "node-ssr","node-ssg","vercel-ssr","vercel-ssg","netlify-ssr","netlify-ssg"'
// expected values:
// node-ssr, node-ssg, vercel-ssr, vercel-ssg, netlify-ssr, netlify-ssg
const hosting = RUNTIME.split('-')[0];
const rt = RUNTIME.split('-')[1];
let ada;
if (hosting === 'vercel') {
	if (rt === 'ssg') {
		ada = vercelStatic({
			analytics: true
		});
	} else if (rt === 'ssr') {
		ada = vercelServerless({
			analytics: true
		});
	} else {
		throw new Error(errMsg);
	}
} else if (hosting === 'node') {
	ada = node({
		mode: 'standalone'
	});
} else if (hosting === 'netlify') {
	if (rt === 'ssg') {
		ada = node({
			mode: 'standalone'
		});
	} else if (rt === 'ssr') {
		ada = netlify()
	} else {
		throw new Error(errMsg);
	}
} else {
	throw new Error(errMsg);
}
const op = rt === 'ssr' ? 'server' : 'static';

// https://astro.build/config
export default defineConfig({
	site: 'https://np.dreambulare.com',
	integrations: [mdx(), sitemap(), image(), partytown({
		config: {
			debug: false
		}
	})],
	output: op,
	adapter: ada
});