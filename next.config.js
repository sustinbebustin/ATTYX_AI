/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  serverRuntimeConfig: {
    apiBearerToken: process.env.API_BEARER_TOKEN
  },
  publicRuntimeConfig: {}
};

module.exports = nextConfig;