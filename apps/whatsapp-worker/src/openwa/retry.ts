export function calculateBackoffMs(
  attemptCount: number,
  initialMs: number = 1000,
  maxMs: number = 60000
): number {
  const exponential = initialMs * Math.pow(2, attemptCount - 1);
  const jitter = Math.random() * 0.2 * exponential;
  return Math.min(maxMs, Math.floor(exponential + jitter));
}
