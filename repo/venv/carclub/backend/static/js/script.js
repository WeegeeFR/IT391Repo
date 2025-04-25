$(document).ready(function () {
    // This is for the navbar link highlight
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

    // This is for auto-dismissing Messages
    setTimeout(function () {
        $(".alert").fadeOut("slow");
    }, 2000); // 5 seconds

    // This is for the buttons on the stats page
    $(".btn").click(function () {
        $(".btn").hide();
        $(".loading").show();
    });


});


