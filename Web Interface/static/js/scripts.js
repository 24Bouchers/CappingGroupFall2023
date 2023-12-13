/*!
    * Start Bootstrap - SB Admin v7.0.7 (https://startbootstrap.com/template/sb-admin)
    * Copyright 2013-2023 Start Bootstrap
    * Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-sb-admin/blob/master/LICENSE)
    */
    // 
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

});

// retrieves the last part of the current URL (index.html, devices.html, ...)
document.addEventListener("DOMContentLoaded", function() {
    var currentPath = window.location.pathname;
    var links = document.querySelectorAll('.nav-link');

    links.forEach(function(link) {
        // Remove the leading slash from the link's href attribute
        var linkPath = link.getAttribute('href').replace(/^\//, '');

        // Check if the current path includes 'addDevice.html' or 'devices.html'
        if (currentPath.includes('addDevice.html') || currentPath.includes('devices.html')) {
            if (linkPath === 'devices.html') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        // Check if the current path includes 'editDevice'
        } else if (currentPath.includes('editDevice')) {
            if (linkPath === 'devices.html') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        // For all other pages
        } else {
            if (currentPath.endsWith(linkPath)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        }
    });
});







