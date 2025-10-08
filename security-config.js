// Legitimate security configurations matching Telegram's policies
const SECURITY_POLICIES = {
  csp: {
    'default-src': ["'self'", 'https://*.telegram.org', 'https://*.t.me', 'https://*.dropbox.com'],
    'img-src': ["'self'", 'data:', 'https://*.telegram.org', 'https://*.t.me', 'https://telegrams.app'],
    'script-src': ["'self'", "'sha256-ACTUAL_HASH'", 'https://*.telegram.org'],
    'style-src': ["'self'", "'unsafe-inline'", 'https://*.telegram.org'],
    'font-src': ["'self'", 'https://*.telegram.org', 'data:'],
    'connect-src': ["'self'", 'https://*.telegram.org', 'https://*.dropbox.com'],
    'frame-src': ['none'],
    'object-src': ['none'],
    'base-uri': ["'none'"],
    'form-action': ["'self'"],
    'frame-ancestors': ["'none'"],
    'upgrade-insecure-requests': []
  },
  
  permissions: {
    'permissions-policy': [
      'accelerometer=()',
      'camera=()',
      'geolocation=()',
      'gyroscope=()',
      'magnetometer=()',
      'microphone=()',
      'payment=()',
      'usb=()'
    ].join(', ')
  },
  
  security: {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Cross-Origin-Resource-Policy': 'same-origin',
    'Cross-Origin-Opener-Policy': 'same-origin'
  }
};

// Legitimate SSL configuration matching Telegram
const SSL_CONFIG = {
  minVersion: 'TLSv1.3',
  cipherSuites: [
    'TLS_AES_128_GCM_SHA256',
    'TLS_AES_256_GCM_SHA384',
    'TLS_CHACHA20_POLY1305_SHA256'
  ],
  honorCipherOrder: true,
  preferServerCiphers: true
};

// DNS CAA Records (to be added to Cloudflare)
const CAA_RECORDS = [
  {
    flags: 0,
    tag: 'issue',
    value: 'letsencrypt.org'
  },
  {
    flags: 0,
    tag: 'iodef',
    value: 'mailto:security@telegrams.app'
  }
];

// Security.txt content
const SECURITY_TXT = `
Contact: mailto:security@telegrams.app
Encryption: https://telegrams.app/pgp-key.txt
Preferred-Languages: en, da
Canonical: https://telegrams.app/.well-known/security.txt
Policy: https://telegrams.app/security-policy
Hiring: https://telegrams.app/security-jobs
`;

module.exports = {
  SECURITY_POLICIES,
  SSL_CONFIG,
  CAA_RECORDS,
  SECURITY_TXT
};