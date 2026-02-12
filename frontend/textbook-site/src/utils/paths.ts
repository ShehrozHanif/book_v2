// Base URL for the site - matches docusaurus.config.js baseUrl
const BASE_URL = '/book_v2';

/**
 * Converts a relative path to an absolute path with the site's base URL
 * @param path - The relative path (should start with /)
 * @returns The full path with base URL prefix
 */
export function siteUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${BASE_URL}${cleanPath}`;
}
