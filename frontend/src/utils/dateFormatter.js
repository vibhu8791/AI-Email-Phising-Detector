/**
 * Consistently format an email timestamp to Asia/Kolkata (IST).
 * Prioritizes date_display from backend, or parses timestamp_utc / created_at / date.
 */
export function formatEmailDateIST(email) {
  if (!email) return 'Unknown';
  if (email.date_display) {
    return email.date_display;
  }
  const raw = email.timestamp_utc || email.created_at || email.date;
  if (!raw) return 'Unknown';
  try {
    const d = new Date(raw);
    if (isNaN(d.getTime())) {
      return email.date || 'Unknown';
    }
    return d.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }) + ' IST';
  } catch (e) {
    return email.date || 'Unknown';
  }
}
