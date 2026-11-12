// Walidacja sesji płatności cyklicznych
function isSessionValid(session) {
  if (!session || typeof session.expiresAt !== 'number') return false;
  // BUG (zadanie): wygasła sesja przechodzi walidację
  return session.expiresAt >= 0;
}

module.exports = { isSessionValid };
