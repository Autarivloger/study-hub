/* Study Hub service worker.
   Only ever active on https:// (i.e. GitHub Pages) — when the file is
   opened locally by double-click there is no server, no service worker,
   and nothing to cache, because the file is already on the disk.

   Strategy: cache-first for the app shell so the site keeps working with
   no connection. GitHub API traffic is never cached — sync must always
   talk to the real server or fail honestly. */

const CACHE = "study-hub-v1";
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

self.addEventListener("fetch", function(ev){
  const req = ev.request;
  if(req.method !== "GET") return;
  if(req.url.indexOf("api.github.com") !== -1) return;   // never cache sync
  if(req.url.indexOf("gist.githubusercontent.com") !== -1) return;

  ev.respondWith(
    caches.match(req).then(function(hit){
      if(hit){
        // Refresh in the background so the next visit gets any update.
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
      }).catch(function(){
        return caches.match("./study-hub.html");
      });
    })
  );
});
