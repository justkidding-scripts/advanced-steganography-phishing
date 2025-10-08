// Legitimate-looking telemetry server
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const TELEMETRY_TYPES = {
  'performance': generatePerformanceData,
  'usage': generateUsageData,
  'network': generateNetworkData,
  'error': generateErrorData
};

async function handleRequest(request) {
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  // Parse telemetry data
  let data;
  try {
    data = await request.json();
  } catch {
    return new Response('Invalid data', { status: 400 });
  }

  // Generate legitimate-looking telemetry response
  const telemetryId = generateTelemetryId();
  const timestamp = new Date().toISOString();
  
  // Generate appropriate response based on telemetry type
  const generator = TELEMETRY_TYPES[data.type] || TELEMETRY_TYPES['usage'];
  const telemetryData = generator(data);

  // Store telemetry with metadata
  const metadata = {
    id: telemetryId,
    timestamp: timestamp,
    client_id: data.client_id || 'unknown',
    version: data.version || '4.12.5',
    platform: data.platform || 'unknown',
    locale: data.locale || 'en-US',
    data: telemetryData
  };

  return new Response(JSON.stringify({
    success: true,
    telemetry_id: telemetryId,
    timestamp: timestamp,
    next_report: Date.now() + 3600000 // 1 hour
  }), {
    headers: {
      'Content-Type': 'application/json',
      'X-Telemetry-Server': 'telemetry/1.0',
      'X-Report-ID': telemetryId
    }
  });
}

function generateTelemetryId() {
  const timestamp = Date.now().toString(36);
  const random = Math.random().toString(36).substr(2, 8);
  return `tlm_${timestamp}_${random}`;
}

function generatePerformanceData(data) {
  return {
    cpu_usage: Math.random() * 15,
    memory_usage: Math.floor(Math.random() * 500) + 200,
    gpu_usage: Math.random() * 10,
    fps: Math.floor(Math.random() * 10) + 55,
    load_time: Math.floor(Math.random() * 1000) + 500,
    render_time: Math.floor(Math.random() * 100) + 50
  };
}

function generateUsageData(data) {
  return {
    active_time: Math.floor(Math.random() * 3600),
    message_count: Math.floor(Math.random() * 100),
    media_sent: Math.floor(Math.random() * 10),
    calls_made: Math.floor(Math.random() * 2),
    features_used: [
      'messaging',
      'media_preview',
      'voice_messages',
      'settings'
    ]
  };
}

function generateNetworkData(data) {
  return {
    connection_type: 'wifi',
    signal_strength: Math.floor(Math.random() * 5) + 1,
    bandwidth: Math.floor(Math.random() * 100) + 50,
    latency: Math.floor(Math.random() * 50) + 20,
    packet_loss: Math.random() * 0.1,
    dns_resolution: Math.floor(Math.random() * 50) + 10
  };
}

function generateErrorData(data) {
  const errors = [
    'NET_ERR_CONNECTION_RESET',
    'MEDIA_DECODE_ERROR',
    'CACHE_MISS',
    'AUTHENTICATION_REQUIRED'
  ];
  
  return {
    error_type: errors[Math.floor(Math.random() * errors.length)],
    severity: Math.floor(Math.random() * 3) + 1,
    count: Math.floor(Math.random() * 5) + 1,
    first_seen: new Date(Date.now() - Math.random() * 86400000).toISOString(),
    last_seen: new Date().toISOString()
  };
}