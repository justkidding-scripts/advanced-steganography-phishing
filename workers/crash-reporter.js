// Legitimate-looking crash reporter
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  // Parse crash report
  let report;
  try {
    report = await request.json();
  } catch {
    return new Response('Invalid report', { status: 400 });
  }

  // Generate legitimate-looking crash ID
  const crashId = generateCrashId();
  
  // Store metadata about the crash (helps look legitimate)
  const metadata = {
    id: crashId,
    timestamp: new Date().toISOString(),
    version: report.version || '4.12.5',
    platform: report.platform || 'unknown',
    process_type: report.process_type || 'browser',
    crash_reason: report.reason || 'SIGSEGV',
    crash_address: '0x' + Math.floor(Math.random() * 16**12).toString(16).padStart(12, '0'),
    crashing_thread: Math.floor(Math.random() * 32),
    stack_traces: {
      threads: [{
        thread_name: 'CrashThread',
        frames: generateFakeStackTrace()
      }]
    }
  };

  // Return legitimate-looking response
  return new Response(JSON.stringify({
    success: true,
    crash_id: crashId,
    timestamp: metadata.timestamp,
    report_url: `https://crashes.telegrams.app/reports/${crashId}`
  }), {
    headers: {
      'Content-Type': 'application/json',
      'X-Crash-Server': 'crash-reporter/1.0',
      'X-Report-ID': crashId
    }
  });
}

function generateCrashId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 8);
  return `${timestamp}_${random}`;
}

function generateFakeStackTrace() {
  const frames = [];
  const modules = ['telegram.dll', 'electron.dll', 'kernel32.dll', 'ntdll.dll'];
  const functions = [
    'TelegramUpdateCheck',
    'RunMessageLoop',
    'ProcessEvents',
    'HandleWindowMessage',
    'DispatchMessage'
  ];

  for (let i = 0; i < 8; i++) {
    frames.push({
      module: modules[Math.floor(Math.random() * modules.length)],
      function: functions[Math.floor(Math.random() * functions.length)],
      file: 'unknown',
      line: Math.floor(Math.random() * 10000),
      offset: '0x' + Math.floor(Math.random() * 16**8).toString(16).padStart(8, '0')
    });
  }

  return frames;
}