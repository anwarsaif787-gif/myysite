/* ==========================================================================
   Osama Sami Physiotherapy — Interactions
   ========================================================================== */
(function () {
    "use strict";

    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    /* ---------- Preloader ---------- */
    var preloader = document.getElementById("preloader");
    function hidePreloader() {
        if (preloader) {
            preloader.classList.add("is-hidden");
        }
    }
    window.addEventListener("load", function () {
        setTimeout(hidePreloader, 350);
    });
    if (document.readyState === "complete") {
        setTimeout(hidePreloader, 350);
    }
    setTimeout(hidePreloader, 3200);

    /* ---------- Header, progress, back to top ---------- */
    var header = document.getElementById("siteHeader");
    var progress = document.getElementById("scrollProgress");
    var backToTop = document.getElementById("backToTop");

    function onScroll() {
        var y = window.scrollY || window.pageYOffset;
        if (header) {
            header.classList.toggle("is-scrolled", y > 24);
        }
        if (progress) {
            var max = document.documentElement.scrollHeight - window.innerHeight;
            progress.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
        }
        if (backToTop) {
            backToTop.classList.toggle("is-visible", y > 520);
        }
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();

    if (backToTop) {
        backToTop.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
        });
    }

    /* ---------- Mobile navigation ---------- */
    var nav = document.getElementById("primaryNav");
    var navToggle = document.getElementById("navToggle");
    var navBackdrop = document.getElementById("navBackdrop");

    function closeNav() {
        if (!nav || !navToggle) return;
        nav.classList.remove("is-open");
        navToggle.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        if (navBackdrop) navBackdrop.classList.remove("is-visible");
        document.body.style.overflow = "";
    }

    if (navToggle && nav) {
        navToggle.addEventListener("click", function () {
            var open = nav.classList.toggle("is-open");
            navToggle.classList.toggle("is-open", open);
            navToggle.setAttribute("aria-expanded", String(open));
            if (navBackdrop) navBackdrop.classList.toggle("is-visible", open);
            document.body.style.overflow = open ? "hidden" : "";
        });
        nav.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", closeNav);
        });
    }
    if (navBackdrop) navBackdrop.addEventListener("click", closeNav);
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape") closeNav();
    });

    /* ---------- Scroll reveal ---------- */
    var revealEls = document.querySelectorAll("[data-reveal]");
    if (!reduceMotion && "IntersectionObserver" in window) {
        var revealObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        var delay = parseInt(entry.target.getAttribute("data-delay") || "0", 10);
                        entry.target.style.transitionDelay = Math.min(delay, 6) * 80 + "ms";
                        entry.target.classList.add("is-visible");
                        revealObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
        );
        revealEls.forEach(function (el) {
            revealObserver.observe(el);
        });
    } else {
        revealEls.forEach(function (el) {
            el.classList.add("is-visible");
        });
    }

    /* ---------- Animated counters ---------- */
    function animateCounter(el) {
        var target = parseInt(el.getAttribute("data-counter") || "0", 10);
        var suffix = el.getAttribute("data-suffix") || "";
        if (reduceMotion) {
            el.textContent = target.toLocaleString() + suffix;
            return;
        }
        var duration = 1700;
        var start = null;
        function step(timestamp) {
            if (!start) start = timestamp;
            var p = Math.min((timestamp - start) / duration, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(target * eased).toLocaleString() + suffix;
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    var counters = document.querySelectorAll("[data-counter]");
    if ("IntersectionObserver" in window) {
        var counterObserver = new IntersectionObserver(
            function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        counterObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.4 }
        );
        counters.forEach(function (el) {
            counterObserver.observe(el);
        });
    } else {
        counters.forEach(animateCounter);
    }

    /* ---------- Accordions ---------- */
    document.querySelectorAll("[data-accordion]").forEach(function (accordion) {
        var items = accordion.querySelectorAll(".accordion__item");
        items.forEach(function (item) {
            var trigger = item.querySelector(".accordion__trigger");
            var panel = item.querySelector(".accordion__panel");
            if (!trigger || !panel) return;
            trigger.addEventListener("click", function () {
                var isOpen = item.classList.contains("is-open");
                items.forEach(function (other) {
                    if (other !== item) {
                        other.classList.remove("is-open");
                        var t = other.querySelector(".accordion__trigger");
                        var p = other.querySelector(".accordion__panel");
                        if (t) t.setAttribute("aria-expanded", "false");
                        if (p) p.style.maxHeight = null;
                    }
                });
                if (isOpen) {
                    item.classList.remove("is-open");
                    trigger.setAttribute("aria-expanded", "false");
                    panel.style.maxHeight = null;
                } else {
                    item.classList.add("is-open");
                    trigger.setAttribute("aria-expanded", "true");
                    panel.style.maxHeight = panel.scrollHeight + "px";
                }
            });
        });
    });

    /* ---------- Testimonial sliders ---------- */
    document.querySelectorAll("[data-slider]").forEach(function (slider) {
        var track = slider.querySelector("[data-slider-track]");
        if (!track) return;
        var scope = slider.closest("section") || document;
        var prev = scope.querySelector("[data-slider-prev]");
        var next = scope.querySelector("[data-slider-next]");

        function step() {
            var card = track.querySelector(".testimonial-card");
            var gap = parseFloat(getComputedStyle(track).columnGap || "24") || 24;
            return (card ? card.offsetWidth : 320) + gap;
        }
        if (prev) {
            prev.addEventListener("click", function () {
                track.scrollBy({ left: -step(), behavior: reduceMotion ? "auto" : "smooth" });
            });
        }
        if (next) {
            next.addEventListener("click", function () {
                track.scrollBy({ left: step(), behavior: reduceMotion ? "auto" : "smooth" });
            });
        }
    });

    /* ---------- Gallery filters ---------- */
    document.querySelectorAll("[data-gallery-filters]").forEach(function (bar) {
        var container = document.querySelector("[data-gallery]");
        if (!container) return;
        bar.querySelectorAll("[data-filter]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                bar.querySelectorAll("[data-filter]").forEach(function (b) {
                    b.classList.remove("is-active");
                });
                btn.classList.add("is-active");
                var filter = btn.getAttribute("data-filter");
                container.querySelectorAll(".gallery-item").forEach(function (item) {
                    var show = filter === "all" || item.getAttribute("data-category") === filter;
                    item.style.display = show ? "" : "none";
                });
            });
        });
    });

    /* ---------- Lightbox ---------- */
    var lightbox = document.createElement("div");
    lightbox.className = "lightbox";
    lightbox.setAttribute("role", "dialog");
    lightbox.setAttribute("aria-modal", "true");
    lightbox.innerHTML =
        '<button class="lightbox__close" type="button" aria-label="Close image">&times;</button>' +
        '<img alt="">' +
        '<div class="lightbox__caption"></div>';
    document.body.appendChild(lightbox);
    var lightboxImg = lightbox.querySelector("img");
    var lightboxCaption = lightbox.querySelector(".lightbox__caption");

    function openLightbox(src, caption) {
        lightboxImg.src = src;
        lightboxImg.alt = caption || "Gallery image";
        lightboxCaption.textContent = caption || "";
        lightbox.classList.add("is-open");
        document.body.style.overflow = "hidden";
    }
    function closeLightbox() {
        lightbox.classList.remove("is-open");
        document.body.style.overflow = "";
        setTimeout(function () {
            lightboxImg.removeAttribute("src");
        }, 300);
    }
    document.addEventListener("click", function (e) {
        var link = e.target.closest("[data-lightbox]");
        if (link) {
            e.preventDefault();
            openLightbox(link.getAttribute("href"), link.getAttribute("data-caption"));
            return;
        }
        if (e.target === lightbox || e.target.closest(".lightbox__close")) {
            closeLightbox();
        }
    });
    document.addEventListener("keydown", function (e) {
        if (e.key === "Escape" && lightbox.classList.contains("is-open")) {
            closeLightbox();
        }
    });

    /* ---------- Booking slot picker ---------- */
    var bookingForm = document.getElementById("bookingForm");
    if (bookingForm) {
        var dateInput = bookingForm.querySelector('input[name="date"]');
        var timeInput = bookingForm.querySelector('input[name="time"]');
        var slotGrid = document.getElementById("slotGrid");
        var slotsUrl = bookingForm.getAttribute("data-slots-url");
        var selectedTime = timeInput ? timeInput.value : "";
        var requestId = 0;

        var loadSlots = function (preselect) {
            if (!dateInput || !slotGrid) return;
            var date = dateInput.value;
            if (!date) {
                slotGrid.innerHTML = '<p class="slot-hint">Choose a date above to see available times.</p>';
                return;
            }
            var current = ++requestId;
            slotGrid.classList.add("is-loading");
            slotGrid.innerHTML = '<p class="slot-hint">Loading available times&hellip;</p>';

            fetch(slotsUrl + "?date=" + encodeURIComponent(date), {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, data: data };
                    });
                })
                .then(function (result) {
                    if (current !== requestId) return;
                    slotGrid.classList.remove("is-loading");
                    if (!result.ok) {
                        slotGrid.innerHTML =
                            '<p class="slot-hint slot-hint--error">' +
                            (result.data.error || "Unable to load times.") +
                            "</p>";
                        return;
                    }
                    var slots = result.data.slots || [];
                    if (!slots.length) {
                        slotGrid.innerHTML =
                            '<p class="slot-hint">No available times for this date. Please choose another day.</p>';
                        if (timeInput) timeInput.value = "";
                        return;
                    }
                    slotGrid.innerHTML = "";
                    slots.forEach(function (slot) {
                        var btn = document.createElement("button");
                        btn.type = "button";
                        btn.className = "slot-btn";
                        btn.textContent = slot.label;
                        btn.setAttribute("data-value", slot.value);
                        if (preselect && preselect === slot.value) {
                            btn.classList.add("is-selected");
                            if (timeInput) timeInput.value = slot.value;
                        }
                        btn.addEventListener("click", function () {
                            slotGrid.querySelectorAll(".slot-btn").forEach(function (b) {
                                b.classList.remove("is-selected");
                            });
                            btn.classList.add("is-selected");
                            if (timeInput) timeInput.value = slot.value;
                        });
                        slotGrid.appendChild(btn);
                    });
                })
                .catch(function () {
                    if (current !== requestId) return;
                    slotGrid.classList.remove("is-loading");
                    slotGrid.innerHTML =
                        '<p class="slot-hint slot-hint--error">Something went wrong. Please try again.</p>';
                });
        };

        if (dateInput) {
            dateInput.addEventListener("change", function () {
                if (timeInput) timeInput.value = "";
                loadSlots();
            });
            if (dateInput.value) {
                loadSlots(selectedTime);
            }
        }
    }

    /* ---------- Auto-dismiss toasts ---------- */
    document.querySelectorAll(".toast").forEach(function (toast) {
        setTimeout(function () {
            toast.style.transition = "opacity .4s ease, transform .4s ease";
            toast.style.opacity = "0";
            toast.style.transform = "translateY(-8px)";
            setTimeout(function () {
                toast.remove();
            }, 400);
        }, 5500);
    });
})();
