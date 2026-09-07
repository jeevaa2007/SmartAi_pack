import { MetadataRoute } from 'next';

/**
 * Standard Next.js sitemap generator mapping public portal links.
 */
export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL || 'https://smartpack.ai';
  
  return [
    {
      url: baseUrl,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    },
    {
      url: `${baseUrl}/verification`,
      lastModified: new Date(),
      changeFrequency: 'always',
      priority: 0.8,
    },
    {
      url: `${baseUrl}/orders`,
      lastModified: new Date(),
      changeFrequency: 'always',
      priority: 0.7,
    },
  ];
}
