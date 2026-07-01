/* ============================================================
   Quantum Fusion POC — interactions
   GSAP + ScrollTrigger when available; graceful fallbacks for
   reduced-motion and CDN failure. Content is never hidden if JS
   or GSAP doesn't run (the .reveal base state is only armed here).
   ============================================================ */
(function () {
  "use strict";

  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasGSAP = typeof window.gsap !== "undefined";
  var hasST = hasGSAP && typeof window.ScrollTrigger !== "undefined";

  /* ---------- Mobile nav ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var links = document.querySelector(".nav-links");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", links.classList.contains("open"));
    });
    links.querySelectorAll("a").forEach(function (a) {
      a.addEventListener("click", function () { links.classList.remove("open"); });
    });
  }

  /* ---------- Accordion (works regardless of motion prefs) ---------- */
  document.querySelectorAll(".acc-q").forEach(function (btn) {
    var item = btn.closest(".acc-item");
    var panel = item.querySelector(".acc-a");
    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function () {
      var isOpen = item.classList.contains("open");
      if (isOpen) {
        item.classList.remove("open");
        btn.setAttribute("aria-expanded", "false");
        if (reduced) { panel.style.height = "0px"; }
        else { animateHeight(panel, panel.scrollHeight, 0); }
      } else {
        item.classList.add("open");
        btn.setAttribute("aria-expanded", "true");
        var target = panel.querySelector(".acc-a-inner").offsetHeight;
        if (reduced) { panel.style.height = "auto"; }
        else { animateHeight(panel, 0, target, function () { panel.style.height = "auto"; }); }
      }
    });
  });
  function animateHeight(el, from, to, done) {
    if (hasGSAP) {
      window.gsap.fromTo(el, { height: from }, { height: to, duration: 0.32, ease: "power2.out", onComplete: done });
    } else {
      el.style.height = to + "px"; if (done) done();
    }
  }

  /* ---------- Progress bar ---------- */
  var bar = document.querySelector(".progress");
  if (bar && !reduced) {
    window.addEventListener("scroll", function () {
      var h = document.documentElement;
      var pct = (h.scrollTop) / (h.scrollHeight - h.clientHeight);
      bar.style.width = (pct * 100) + "%";
    }, { passive: true });
  }

  /* ---------- Reveals ---------- */
  function showAll() {
    document.querySelectorAll(".reveal, .reveal-stagger").forEach(function (el) { el.classList.add("in"); });
  }

  if (reduced || !hasST) {
    // Fallback: IntersectionObserver so things still animate softly without GSAP,
    // or just show everything under reduced-motion.
    if (reduced || !("IntersectionObserver" in window)) {
      showAll();
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
      }, { rootMargin: "0px 0px -10% 0px", threshold: 0.1 });
      document.querySelectorAll(".reveal, .reveal-stagger").forEach(function (el) { io.observe(el); });
    }
    // Counters: snap to final value
    document.querySelectorAll("[data-count]").forEach(function (el) { el.textContent = el.getAttribute("data-count-display") || el.getAttribute("data-count"); });
  } else {
    var gsap = window.gsap, ST = window.ScrollTrigger;
    gsap.registerPlugin(ST);

    // Simple reveals
    gsap.utils.toArray(".reveal").forEach(function (el) {
      ST.create({
        trigger: el, start: "top 85%",
        onEnter: function () { el.classList.add("in"); }
      });
    });
    // Staggered groups
    gsap.utils.toArray(".reveal-stagger").forEach(function (group) {
      var kids = group.children;
      ST.create({
        trigger: group, start: "top 82%",
        onEnter: function () {
          group.classList.add("in");
          gsap.fromTo(kids, { y: 18, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, stagger: 0.08, ease: "power2.out" });
        }
      });
    });

    // Count-ups
    gsap.utils.toArray("[data-count]").forEach(function (el) {
      var end = parseFloat(el.getAttribute("data-count"));
      var dec = parseInt(el.getAttribute("data-decimals") || "0", 10);
      var prefix = el.getAttribute("data-prefix") || "";
      var suffix = el.getAttribute("data-suffix") || "";
      var obj = { v: 0 };
      ST.create({
        trigger: el, start: "top 88%", once: true,
        onEnter: function () {
          gsap.to(obj, {
            v: end, duration: 1.4, ease: "power2.out",
            onUpdate: function () { el.textContent = prefix + obj.v.toFixed(dec) + suffix; },
            onComplete: function () { el.textContent = el.getAttribute("data-count-display") || (prefix + end.toFixed(dec) + suffix); }
          });
        }
      });
    });

    // Draw-on SVG paths (class .draw)
    gsap.utils.toArray(".draw").forEach(function (path) {
      var len = path.getTotalLength ? path.getTotalLength() : 0;
      if (!len) return;
      gsap.set(path, { strokeDasharray: len, strokeDashoffset: len });
      ST.create({
        trigger: path, start: "top 85%", once: true,
        onEnter: function () { gsap.to(path, { strokeDashoffset: 0, duration: 1.6, ease: "power1.inOut" }); }
      });
    });

    // Hero intro
    var heroBits = gsap.utils.toArray("[data-hero]");
    if (heroBits.length) {
      gsap.fromTo(heroBits, { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, stagger: 0.12, ease: "power3.out", delay: 0.1 });
    }

    // Pinned horizontal ladder (notebooks). Opt-in via [data-pin-ladder].
    var ladder = document.querySelector("[data-pin-ladder]");
    if (ladder && window.innerWidth > 900) {
      var track = ladder.querySelector(".ladder-track");
      var panels = track ? track.children.length : 0;
      if (track && panels > 1) {
        var shift = function () { return track.scrollWidth - ladder.offsetWidth; };
        gsap.to(track, {
          x: function () { return -shift(); }, ease: "none",
          scrollTrigger: {
            trigger: ladder, start: "top top", end: function () { return "+=" + shift(); },
            scrub: 0.6, pin: true, anticipatePin: 1, invalidateOnRefresh: true
          }
        });
      }
    }
  }
})();
