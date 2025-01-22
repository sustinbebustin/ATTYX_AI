/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  serverRuntimeConfig: {
    API_BEARER_TOKEN: process.env.API_BEARER_TOKEN
  },
  publicRuntimeConfig: {}
};

module.exports = nextConfig;