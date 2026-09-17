  function openModal() {
    document.getElementById('demoModal').classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeModal() {
    document.getElementById('demoModal').classList.remove('open');
    document.body.style.overflow = '';
  }
  document.getElementById('demoModal').addEventListener('click', function(e) {
    if (e.target === this) closeModal();
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeModal();
  });

  function toggleMobileNav() {
    var nav = document.getElementById('mobileNav');
    var btn = document.getElementById('hamburger');
    nav.classList.toggle('open');
    btn.classList.toggle('open');
  }
  function closeMobileNav() {
    document.getElementById('mobileNav').classList.remove('open');
    document.getElementById('hamburger').classList.remove('open');
  }

  function showPrivacy() {
    document.getElementById('main-site').style.display = 'none';
    document.getElementById('privacy-page').classList.add('show');
    window.scrollTo(0, 0);
  }

  function showMain() {
    document.getElementById('main-site').style.display = 'block';
    document.getElementById('privacy-page').classList.remove('show');
    window.scrollTo(0, 0);
  }

  /* Privacy sidebar scroll-spy */
  (function() {
    var sections = ['pp-1','pp-2','pp-3','pp-4','pp-5','pp-6','pp-7','pp-8','pp-9','pp-10','pp-11','pp-12','pp-13'];
    var navLinks = {};
    sections.forEach(function(id) {
      var link = document.querySelector('#privacyNav a[href="#' + id + '"]');
      if (link) navLinks[id] = link;
    });
    function onScroll() {
      var scrollY = window.pageYOffset + 120;
      var active = sections[0];
      sections.forEach(function(id) {
        var el = document.getElementById(id);
        if (el && el.offsetTop <= scrollY) active = id;
      });
      Object.keys(navLinks).forEach(function(id) {
        navLinks[id].classList.toggle('active', id === active);
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
  })();

  /* Auto-show privacy page if ?page=privacy in URL */
  (function() {
    var params = new URLSearchParams(window.location.search);
    if (params.get('page') === 'privacy') {
      showPrivacy();
    }
  })();
