$(document).ready(function () {
    // Get the current URL path
    let currentPath = window.location.pathname;

    // Loop through each navigation link
    $('nav a').each(function () {
        // Get the href attribute of the link
        let linkHref = $(this).attr('href');

        // Check if the link's href matches the current URL path
        if (currentPath === linkHref) {
            // Add the 'active' class to the matching link
            $(this).addClass('active');
        } else {
            //If not the current page, remove the active class
            $(this).removeClass('active');
        }
    });

    $('#menu-icon').click(function () {
        $(this).toggleClass('bx-x');
        $('header nav').toggleClass('active');
    });
});


