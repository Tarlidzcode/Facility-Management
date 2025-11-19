export function notFoundHandler(req, res, next) {
  res.status(404).json({ error: 'Route not found.' });
}

export function errorHandler(err, req, res, next) {
  const status = typeof err.status === 'number' ? err.status : 500;
  const message = status === 500 ? 'Internal server error.' : err.message;

  console.error('Azure chat service error:', err);

  res.status(status).json({ error: message });
}
