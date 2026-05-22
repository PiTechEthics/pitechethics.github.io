// Highlight the nav link for whichever section is currently in view.
(function () {
    var links = Array.prototype.slice.call(document.querySelectorAll('.nav-links a'));
    if (!('IntersectionObserver' in window) || links.length === 0) return;

    var byId = {};
    links.forEach(function (link) {
        var id = link.getAttribute('href').slice(1);
        byId[id] = link;
    });

    var sections = Object.keys(byId)
        .map(function (id) { return document.getElementById(id); })
        .filter(Boolean);

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            links.forEach(function (l) { l.classList.remove('active'); });
            var active = byId[entry.target.id];
            if (active) active.classList.add('active');
        });
    }, { rootMargin: '-45% 0px -50% 0px', threshold: 0 });

    sections.forEach(function (section) { observer.observe(section); });
})();
