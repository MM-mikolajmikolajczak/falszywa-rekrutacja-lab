const config = require('./config');
const { isSessionValid } = require('./auth');

console.log(`[FinTech Gateway] ${config.appName} ${config.version} nasłuchuje na porcie ${config.port}`);
console.log('[FinTech Gateway] sesja testowa ważna:', isSessionValid({ expiresAt: Date.now() + 1000 }));
