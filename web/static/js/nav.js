var nav = document.getElementById('nav-button'),
    body = document.body;

nav.addEventListener('click', function (e) {
    body.className = body.className ? '' : 'with_nav';
    e.preventDefault();
});
