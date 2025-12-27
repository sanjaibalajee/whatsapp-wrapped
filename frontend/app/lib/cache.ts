// Cache utility for WhatsApp Wrapped stats

const CACHE_KEY = "wrappedStatsCache";
const CACHE_EXPIRY_HOURS = 24; // Cache expires after 24 hours

interface CachedData {
  stats: {
    slides: unknown[];
    metadata?: Record<string, unknown>;
  };
  metadata?: Record<string, unknown>;
  timestamp: number;
  jobId: string;
}

export function hasValidCache(): boolean {
  if (typeof window === "undefined") return false;

  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return false;

    const data: CachedData = JSON.parse(cached);
    const now = Date.now();
    const expiryTime = CACHE_EXPIRY_HOURS * 60 * 60 * 1000;

    // Check if cache is expired
    if (now - data.timestamp > expiryTime) {
      clearCache();
      return false;
    }

    // Validate that we have the required data
    if (!data.stats?.slides || data.stats.slides.length === 0) {
      clearCache();
      return false;
    }

    return true;
  } catch {
    clearCache();
    return false;
  }
}

export function getCachedStats(): CachedData | null {
  if (typeof window === "undefined") return null;

  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;

    const data: CachedData = JSON.parse(cached);
    return data;
  } catch {
    return null;
  }
}

export function setCachedStats(
  stats: { slides: unknown[]; metadata?: Record<string, unknown> },
  metadata: Record<string, unknown> | undefined,
  jobId: string
): void {
  if (typeof window === "undefined") return;

  try {
    const cacheData: CachedData = {
      stats,
      metadata,
      timestamp: Date.now(),
      jobId,
    };
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData));
  } catch {
    // Storage might be full, ignore
  }
}

export function clearCache(): void {
  if (typeof window === "undefined") return;

  try {
    localStorage.removeItem(CACHE_KEY);
    localStorage.removeItem("wrappedJobId");
    localStorage.removeItem("wrappedParticipants");
  } catch {
    // Ignore errors
  }
}
