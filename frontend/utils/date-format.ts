/**
 * Formats a date in a relative way:
 * - If less than 24 hours ago: "X hours ago"
 * - If yesterday: "yesterday"
 * - If within the last week: "X days ago"
 * - Otherwise: "Month Day" (e.g., "May 15")
 * 
 * Properly handles UTC dates from the backend and accounts for timezone
 * differences between server and client.
 */
export function formatRelativeTime(dateString: string | null): string {
  if (!dateString) return '';
  
  try {
    // Check for incorrect year (2025) in the date string
    if (dateString.includes('2025-')) {
      // Replace 2025 with current year
      const currentYear = new Date().getFullYear();
      dateString = dateString.replace('2025-', `${currentYear}-`);
    }
    
    // Get the current time for comparison
    const now = new Date();
    
    // Parse the date string from the backend (which is in UTC)
    // The 'Z' at the end ensures it's interpreted as UTC
    let date = new Date(dateString.replace(/\.\d+$/, 'Z'));
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return '';
    }
    
    // Calculate time difference in milliseconds
    const diffMs = now.getTime() - date.getTime();
    
    // If the date is in the future (server time ahead of client), treat as very recent
    if (diffMs < 0) {
      return 'just now';
    }
    
    // Use the absolute value for calculations
    const absDiffMs = Math.abs(diffMs);
    
    // If the difference is very small, show "just now"
    if (absDiffMs < 60000) {
      return 'just now';
    }
    
    // Calculate time differences
    const diffMinutes = Math.floor(absDiffMs / (1000 * 60));
    const diffHours = Math.floor(absDiffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(absDiffMs / (1000 * 60 * 60 * 24));
    
    // Check if the date is today or yesterday using calendar date
    const nowDate = now.getDate();
    const nowMonth = now.getMonth();
    const nowYear = now.getFullYear();
    
    const dateDate = date.getDate();
    const dateMonth = date.getMonth();
    const dateYear = date.getFullYear();
    
    const isToday = nowDate === dateDate && nowMonth === dateMonth && nowYear === dateYear;
    
    const yesterday = new Date(now);
    yesterday.setDate(yesterday.getDate() - 1);
    const isYesterday = yesterday.getDate() === dateDate && 
                        yesterday.getMonth() === dateMonth && 
                        yesterday.getFullYear() === dateYear;
    
    // Simple time-based formatting
    if (isToday) {
      if (diffHours < 1) {
        return `${diffMinutes} minutes ago`;
      } else {
        return diffHours === 1 ? '1 hour ago' : `${diffHours} hours ago`;
      }
    }
    
    if (isYesterday) {
      return 'yesterday';
    }
    
    if (diffDays < 7) {
      return `${diffDays} days ago`;
    }
    
    // For older dates, show the formatted date
    const isCurrentYear = dateYear === nowYear;
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: isCurrentYear ? undefined : 'numeric'
    });
  } catch (error) {
    return '';
  }
} 