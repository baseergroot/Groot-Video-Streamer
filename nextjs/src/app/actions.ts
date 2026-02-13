'use server';

export async function fetchVideoInfo(url: string) {
  if (!url) {
    throw new Error('Missing URL.');
  }
  const API_URL = process.env.API_URL || 'http://localhost:8000';
  const apiUrl = `${API_URL}/info`;
  const response = await fetch(`${apiUrl}?url=${encodeURIComponent(url)}`);
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to fetch video info.');
  }
  const data = await response.json();
  // Proxy the thumbnail URL to bypass CORS
  if (data.thumbnail) {
    data.thumbnail = `${API_URL}/proxy-image?url=${encodeURIComponent(data.thumbnail)}`;
  }
  return data;
}

export async function getStreamUrl(url: string) {
  if (!url) {
    throw new Error('Missing URL.');
  }
  const API_URL = process.env.API_URL || 'http://localhost:8000';
  return `${API_URL}/stream?url=${encodeURIComponent(url)}`;
}

export async function getDownloadUrl(url: string, title?: string) {
  if (!url) {
    throw new Error('Missing URL.');
  }
  const API_URL = process.env.API_URL || 'http://localhost:8000';
  const params = new URLSearchParams({ url });
  if (title) {
    params.set('title', title);
  }
  return `${API_URL}/download?${params.toString()}`;
}
