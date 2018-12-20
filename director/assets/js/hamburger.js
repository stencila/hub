
var hamburger = document.querySelector(".hamburger");
var dropdown = document.querySelector("#dropdown-menu");

hamburger.addEventListener("click", function() {
    hamburger.classList.toggle("is-active");
    dropdown.classList.toggle("is-active");
});