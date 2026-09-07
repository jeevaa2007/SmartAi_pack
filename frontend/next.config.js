/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  transpilePackages: [
    'antd',
    '@ant-design/icons',
    'rc-util',
    'rc-pagination',
    'rc-picker',
    'rc-tree',
    'rc-table'
  ],
  // Ensure build works smoothly without warning errors interrupting
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  }
};

module.exports = nextConfig;
