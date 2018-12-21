
var hamburger = document.querySelector(".hamburger");
var dropdown = document.querySelector("#dropdown-menu");


if (hamburger !== null) {
    hamburger.addEventListener("click", function() {
        hamburger.classList.toggle("is-active");
        dropdown.classList.toggle("is-active");
    });
}
