/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  serverRuntimeConfig: {
    API_BEARER_TOKEN: process.env.API_BEARER_TOKEN
  },
  publicRuntimeConfig: {},
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*'
      }
    ]
  }
};

module.exports = nextConfig;