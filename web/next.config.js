/** @type {import('next').NextConfig} */
const repo = process.env.NEXT_PUBLIC_BASE_PATH || "";
const nextConfig = {
  output: "export",
  images: { unoptimized: true },
  basePath: repo,
  assetPrefix: repo || undefined,
  trailingSlash: true,
};
module.exports = nextConfig;
