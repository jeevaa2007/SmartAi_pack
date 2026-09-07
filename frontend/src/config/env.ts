/**
 * Frontend environment variables config parsing.
 * Accesses NEXT_PUBLIC_ prefixes exposed to the browser client.
 */

if (!process.env.NEXT_PUBLIC_API_URL) {
  console.warn("NEXT_PUBLIC_API_URL is not set. Defaulting to local endpoint: http://localhost:8000/api/v1");
}

export const ENV = {
  API_URL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  NODE_ENV: process.env.NODE_ENV || "development",
};
