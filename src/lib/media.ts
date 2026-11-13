const youtubeHosts = new Set([
  "youtube.com",
  "www.youtube.com",
  "m.youtube.com",
  "youtube-nocookie.com",
  "www.youtube-nocookie.com",
  "youtu.be",
]);

export function isHttpUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" || url.protocol === "http:";
  } catch {
    return false;
  }
}

export function youtubeVideoId(value: string) {
  try {
    const url = new URL(value);
    if (!youtubeHosts.has(url.hostname.toLowerCase())) return undefined;

    const id = url.hostname.toLowerCase() === "youtu.be"
      ? url.pathname.split("/").filter(Boolean)[0]
      : url.searchParams.get("v") ?? url.pathname.match(/^\/(?:embed|shorts)\/([^/]+)/)?.[1];

    return id && /^[A-Za-z0-9_-]{11}$/.test(id) ? id : undefined;
  } catch {
    return undefined;
  }
}

export function isSafeMp4Url(value: string) {
  try {
    const url = new URL(value);
    return (url.protocol === "https:" || url.protocol === "http:") &&
      url.pathname.toLowerCase().endsWith(".mp4");
  } catch {
    return false;
  }
}
