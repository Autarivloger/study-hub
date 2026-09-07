/* Study Hub service worker.
   Only ever active on https:// (i.e. GitHub Pages) — when the file is
   opened locally by double-click there is no server and no service worker,
   because the file is already on the disk.

   Strategy, and why it is split:

   - The PAGE ITSELF is network-first. The app is one big HTML file that
     changes every time a lesson is added, so serving a cached copy first
     meant an update only appeared on the SECOND visit. Going to the
     network first means an online visitor always gets the newest lesson,
     and the cached copy is still there as a fallback when offline.

   - Everything else is cache-first, since the icon and manifest almost
     never change and are worth serving instantly.

   - GitHub API traffic is never cached: sync must talk to the real server
     or fail honestly. */

const CACHE = "study-hub-v2";
const SHELL = [
  "./",
  "./index.html",
  "./study-hub.html",
  "./manifest.webmanifest",
  "./icon.svg"
];

self.addEventListener("install", function(ev){
  ev.waitUntil(
    caches.open(CACHE)
      .then(function(c){ return c.addAll(SHELL); })
      .then(function(){ return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function(ev){
  ev.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.map(function(k){
        return k === CACHE ? null : caches.delete(k);
      }));
    }).then(function(){ return self.clients.claim(); })
  );
});

function isPage(req){
  return req.mode === "navigate" ||
         (req.headers.get("accept") || "").indexOf("text/html") !== -1;
}

self.addEventListener("fetch", function(ev){
  const req = ev.request;
  if(req.method !== "GET") return;
  if(req.url.indexOf("api.github.com") !== -1) return;          // never cache sync
  if(req.url.indexOf("gist.githubusercontent.com") !== -1) return;

  if(isPage(req)){
    // Network first: always show the newest lessons when there is a signal.
    ev.respondWith(
      fetch(req).then(function(res){
        if(res && res.ok){
          const copy = res.clone();
          caches.open(CACHE).then(function(c){ c.put(req, copy); });
        }
        return res;
      }).catch(function(){
        return caches.match(req).then(function(hit){
          return hit || caches.match("./study-hub.html");
        });
      })
    );
    return;
  }

  // Everything else: cache first, refreshed quietly in the background.
  ev.respondWith(
    caches.match(req).then(function(hit){
      if(hit){
        fetch(req).then(function(res){
          if(res && res.ok) caches.open(CACHE).then(function(c){ c.put(req, res.clone()); });
        }).catch(function(){});
        return hit;
      }
      return fetch(req).then(function(res){
        if(res && res.ok && req.url.indexOf("http") === 0){
          const copy = res.clone();
          caches.open(CACHE).then(function(c){ c.put(req, copy); });
        }
        return res;
      });
    })
  );
});
