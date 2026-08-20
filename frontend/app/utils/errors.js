export function getErrorMessage(error, fallback = 'Une erreur est survenue.') {
  const detail = error?.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg).filter(Boolean).join(' ')
  }
  return detail || fallback
}