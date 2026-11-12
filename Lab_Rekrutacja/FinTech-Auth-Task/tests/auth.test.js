const assert = require('assert');
const { isSessionValid } = require('../src/auth');

assert.strictEqual(isSessionValid({ expiresAt: Date.now() + 60000 }), true, 'aktywna sesja');
assert.strictEqual(isSessionValid({ expiresAt: Date.now() - 60000 }), false, 'wygasła sesja');
console.log('OK: 2 testy');
