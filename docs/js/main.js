(function () {
  'use strict';

  // Mobile nav toggle
  const toggle = document.getElementById('nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      navLinks.classList.toggle('open');
    });

    navLinks.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        navLinks.classList.remove('open');
      });
    });
  }

  // Copy setup commands
  const copyBtn = document.getElementById('copy-btn');
  const setupCode = document.getElementById('setup-code');

  if (copyBtn && setupCode) {
    copyBtn.addEventListener('click', function () {
      navigator.clipboard.writeText(setupCode.textContent.trim()).then(function () {
        copyBtn.textContent = 'Copied!';
        copyBtn.classList.add('copied');
        setTimeout(function () {
          copyBtn.textContent = 'Copy commands';
          copyBtn.classList.remove('copied');
        }, 2000);
      });
    });
  }

  // Auto-detect GitHub repo URL from meta or current path
  const githubLink = document.getElementById('github-link');
  if (githubLink) {
    const meta = document.querySelector('meta[name="github-repo"]');
    if (meta && meta.content) {
      githubLink.href = meta.content;
    }
  }

  // Fade-in on scroll
  const observer = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    },
    { threshold: 0.1 }
  );

  document.querySelectorAll('.card, .arch-step, .test-item').forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(16px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });
})();