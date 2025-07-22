const routes = [
  { hash: '#home', page: 'home.html' },
  { hash: '#login', page: 'login.html' },
  { hash: '#register', page: 'register.html' },
  { hash: '#profile', page: 'profile.html' },
  { hash: '#discover', page: 'discover.html' },
  { hash: '#chat', page: 'chat.html' },
  { hash: '#orders', page: 'orders.html' },
  { hash: '#admin', page: 'admin.html' }
];

function setActiveNav(hash) {
  document.querySelectorAll('nav ul li a').forEach(a => {
    if (a.getAttribute('href') === hash) {
      a.classList.add('active');
    } else {
      a.classList.remove('active');
    }
  });
}

function loadPage(page, hash) {
  fetch(`pages/${page}`)
    .then(res => res.text())
    .then(html => {
      document.getElementById('app-content').innerHTML = html;
      setActiveNav(hash);
      // Add cross-links for login/register
      if (hash === '#login') {
        const regLink = document.createElement('p');
        regLink.innerHTML = "Don't have an account? <a href='#register' id='to-register'>Register here</a>";
        document.getElementById('app-content').appendChild(regLink);
      } else if (hash === '#register') {
        const loginLink = document.createElement('p');
        loginLink.innerHTML = "Already have an account? <a href='#login' id='to-login'>Login here</a>";
        document.getElementById('app-content').appendChild(loginLink);
      }
    });
}

function router() {
  const hash = window.location.hash || '#home';
  const route = routes.find(r => r.hash === hash);
  if (route) {
    loadPage(route.page, hash);
  } else {
    loadPage('home.html', '#home');
  }
}

window.addEventListener('hashchange', router);
window.addEventListener('DOMContentLoaded', router); 