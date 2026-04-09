const DEV_API_BASE_URL = 'http://localhost:8000';

const configuredApiBaseUrl = import.meta.env.VITE_API_URL?.trim();

function normalizeApiBaseUrl(value: string): string {
  return value.replace(/\/+$/, '');
}

function parseConfiguredApiBaseUrl(value: string): string | null {
  try {
    const url = new URL(value);

    if (url.protocol !== 'http:' && url.protocol !== 'https:') {
      return null;
    }

    return normalizeApiBaseUrl(url.toString());
  } catch {
    return null;
  }
}

const validConfiguredApiBaseUrl = configuredApiBaseUrl
  ? parseConfiguredApiBaseUrl(configuredApiBaseUrl)
  : null;

export const apiConfigurationError =
  !configuredApiBaseUrl && !import.meta.env.DEV
    ? 'The backend API is unavailable because this deployment is missing VITE_API_URL.'
    : configuredApiBaseUrl && !validConfiguredApiBaseUrl
      ? 'The backend API is unavailable because VITE_API_URL must be an absolute http(s) URL.'
      : null;

function requireApiBaseUrl(): string {
  if (validConfiguredApiBaseUrl) {
    return validConfiguredApiBaseUrl;
  }

  if (!configuredApiBaseUrl && import.meta.env.DEV) {
    return DEV_API_BASE_URL;
  }

  if (configuredApiBaseUrl) {
    throw new Error('VITE_API_URL must be an absolute URL starting with http:// or https://.');
  }

  throw new Error('VITE_API_URL must be set to the public backend URL for production deployments.');
}

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${requireApiBaseUrl()}${normalizedPath}`;
}

export function buildWebSocketUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const apiBaseUrl = requireApiBaseUrl();

  if (apiBaseUrl.startsWith('https://')) {
    return `wss://${apiBaseUrl.slice('https://'.length)}${normalizedPath}`;
  }

  if (apiBaseUrl.startsWith('http://')) {
    return `ws://${apiBaseUrl.slice('http://'.length)}${normalizedPath}`;
  }

  throw new Error('VITE_API_URL must start with http:// or https://.');
}
