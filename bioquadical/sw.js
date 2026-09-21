/* The lid on the jar.

   Everything the app needs is already inside index.html — the audio, the
   images, and now the typefaces too. What was missing was any instruction to
   the browser to hold onto it. Without one, an installed copy leans on the
   ordinary HTTP cache, which is free to be cleared at any time and usually is,
   so tapping the home-screen icon offline could just as easily show nothing.

   This keeps the shell on disk permanently and serves it from there first.
   The specimen itself is not in here; that lives in storage, and survives
   independently of anything this file does.

   ---------------------------------------------------------------------------
   2026-09-07: rewritten after this worker took the live Cloudflare deploy down
   with ERR_FAILED on every navigation.

   Netlify and Cloudflare do not serve the same bytes for the same paths.
   Cloudflare's static-asset handler redirects '/index.html' to '/' by default,
   and a redirect is poison in two separate places here:

     - cache.addAll() is all-or-nothing AND rejects on a redirected response,
       so one entry could fail the entire install.
     - a redirected response handed back to a navigation's respondWith() is a
       network error by spec, which Chrome reports as ERR_FAILED.

   Both are now impossible. Nothing in this file can reject a respondWith, no
   single cache entry can fail the install, and every response is rebuilt from
   its own bytes before it is stored or served, which strips the redirect flag
   and any other property that could make it unusable later.

   The rule this file now follows: a broken worker must degrade to being a
   useless worker, never to being a worker that breaks the site. */

/* Bumped together, every deploy. VERSION names the cache; if it does not
   change, the old cache is never replaced. BUILD only ever goes up, so a
   screenshot of the corner of somebody's screen tells you which release they
   are actually running. */
const VERSION = 'v2026.09.09.058';
const BUILD = 61;

const CACHE = 'bq-' + VERSION;

/* './' is the only entry point cached, deliberately. The home-screen launch
   asks for the directory and a reload asks for the file, but on Cloudflare
   './index.html' is a redirect to './', so caching both means caching one good
   copy and one landmine. Navigations are matched against './' below, which
   both requests resolve to. */
const ROOT = './';

/* Optional extras. Every one of these is added on its own: a file that 404s,
   or that is renamed and forgotten, costs exactly itself and nothing else. */
const SHELL = [
  './manifest.webmanifest',
  './apple-touch-icon.png',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './favicon-48.png',
  './bd/abyss-far.webp',
  './bd/abyss-mid.webp',
  './bd/abyss-near.webp',
  './bd/reef-far.webp',
  './bd/reef-mid.webp',
  './bd/reef-near.webp',
  './bd/shallow-far.webp',
  './bd/shallow-mid.webp',
  './bd/shallow-near.webp',
  './bd/wreck-far.webp',
  './bd/city-far.webp',
  './bd/cliff-near.webp',
  './bd/saucer-far.webp',
  './bd/spires-far.webp',
  './bd/moai-far.webp',
  './bd/drowned-far.webp',
  './bd/fair-far.webp',
  './sfx/pet.mp3',
  './sfx/glass.mp3',
  './sfx/hunt.mp3',
  './sfx/hurt.mp3',
  './sfx/hurt2.mp3',
  './sfx/snore.mp3',
  './sfx/spin.mp3',
  './sfx/splash-big.mp3',
];

/* A response that came back through a redirect carries that fact with it, and
   the fact is fatal in a cache and fatal in a navigation. Reading the body out
   and building a fresh response around it discards the history and keeps the
   part that matters. Bodies here are a few megabytes at most and this runs
   once per file per release, so the copy is affordable. */
async function clean(res) {
  if (!res) return null;
  if (!res.redirected && res.type !== 'opaqueredirect') return res;
  const body = await res.blob();
  /* Content-Length and Content-Encoding described the bytes on the wire, not
     the decoded blob now being handed on. Carrying either forward describes a
     body that no longer exists. */
  const headers = new Headers(res.headers);
  headers.delete('content-length');
  headers.delete('content-encoding');
  return new Response(body, { status: 200, statusText: 'OK', headers });
}

/* Fetch and store one path, and never throw. Returns true only if the file is
   genuinely on disk afterwards. */
async function put(cache, path) {
  try {
    const res = await fetch(new Request(path, { cache: 'reload' }));
    if (!res || !res.ok) return false;
    const safe = await clean(res);
    await cache.put(path, safe);
    return true;
  } catch (err) {
    return false;
  }
}

self.addEventListener('install', e => {
  /* The worker this one replaces may be the broken one, in which case waiting
     politely for the page to say 'skipWaiting' waits forever: the page never
     loads, so it never gets to say anything. Taking over immediately is the
     only way a bad release can be recovered from without the user knowing to
     open devtools. */
  self.skipWaiting();

  e.waitUntil((async () => {
    const cache = await caches.open(CACHE);

    /* The root is the one thing worth caring about. If it cannot be stored
       there is no offline app, but there is still a working online one, so
       even this does not fail the install. */
    await put(cache, ROOT);

    /* allSettled, not all: the extras are extras. */
    await Promise.allSettled(SHELL.map(p => put(cache, p)));
  })());
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter(k => k.startsWith('bq-') && k !== CACHE).map(k => caches.delete(k))
      );
    } catch (err) { /* a cache that will not enumerate is not worth dying over */ }
    await self.clients.claim();
  })());
});

/* Served when there is no cached copy and no network. Plain, small, and honest
   about what happened, which beats the browser's own error page because that
   one implies the site is gone. */
function offlinePage() {
  return new Response(
    '<!doctype html><meta charset="utf-8">' +
    '<meta name="viewport" content="width=device-width,initial-scale=1">' +
    '<title>Bioquadical</title>' +
    '<body style="margin:0;display:grid;place-items:center;height:100vh;' +
    'background:#06121a;color:#8fb8c8;font:15px/1.5 system-ui,sans-serif">' +
    '<div style="text-align:center;padding:24px">' +
    '<p>The tank is offline.</p>' +
    '<p style="opacity:.6">Reconnect and reload.</p></div>',
    { status: 200, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
  );
}

self.addEventListener('fetch', e => {
  const req = e.request;

  /* Only our own GETs. Anything else — a POST, another origin — is passed
     through untouched rather than being guessed at. */
  if (req.method !== 'GET') return;
  let url;
  try { url = new URL(req.url); } catch (err) { return; }
  if (url.origin !== self.location.origin) return;

  /* A navigation is a request for the app, whatever path it names. Every
     branch below returns a real response; none of them can reject, because a
     rejected respondWith on a navigation is exactly the ERR_FAILED this file
     was rewritten to make impossible. */
  if (req.mode === 'navigate') {
    e.respondWith((async () => {
      try {
        const hit = await caches.match(ROOT);
        if (hit) return hit;
      } catch (err) { /* fall through to the network */ }

      /* Note the plain URL rather than the navigation request itself: the
         navigation carries redirect mode 'manual', and re-issuing it can hand
         back an opaqueredirect, which is unusable here. Asking for the root
         directly gets an ordinary, followable response. */
      try {
        const net = await fetch(ROOT, { cache: 'no-store' });
        if (net && net.ok) {
          const safe = await clean(net);
          /* Cloned here, synchronously, while the body is still untouched.
             Cloning inside the .then below would race the return: the page
             starts reading the body first and the clone throws. */
          const copy = safe.clone();
          caches.open(CACHE).then(c => c.put(ROOT, copy)).catch(() => {});
          return safe;
        }
      } catch (err) { /* fall through to the offline page */ }

      return offlinePage();
    })());
    return;
  }

  e.respondWith((async () => {
    try {
      const hit = await caches.match(req, { ignoreSearch: true });
      if (hit) return hit;
    } catch (err) { /* fall through to the network */ }

    try {
      return await fetch(req);
    } catch (err) {
      return new Response('', { status: 504, statusText: 'offline' });
    }
  })());
});

/* The page decides when the swap happens, so it can save first and so it never
   happens mid-sentence while someone is watching. install() now also calls
   skipWaiting() on its own, which makes this the polite path rather than the
   only one; a release that breaks the page can still replace itself. */
self.addEventListener('message', e => {
  if (e.data === 'skipWaiting') self.skipWaiting();
  else if (e.data === 'version' && e.source) {
    e.source.postMessage({ ver: VERSION, build: BUILD });
  }
});
