window.onscroll = function() {
    const navbar = document.querySelector(".navbar-custom");

    if (window.pageYOffset > 0) {
        navbar.classList.add("transparent");
    } else {
        navbar.classList.remove("transparent");
    }
};
