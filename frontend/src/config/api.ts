const DEV_API_BASE_URL = 'http://localhost:8000';

const configuredApiBaseUrl = import.meta.env.VITE_API_URL?.trim();

function normalizeApiBaseUrl(value: string): string {
  return value.replace(/\/+$/, '');
}

export const apiConfigurationError =
  !configuredApiBaseUrl && !import.meta.env.DEV
    ? 'Authentication is unavailable because this deployment is missing VITE_API_URL.'
    : null;

function requireApiBaseUrl(): string {
  if (configuredApiBaseUrl) {
    return normalizeApiBaseUrl(configuredApiBaseUrl);
  }

  if (import.meta.env.DEV) {
    return DEV_API_BASE_URL;
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
