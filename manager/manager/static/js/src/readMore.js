const toggle = (e) => {
  e.preventDefault();
  e.currentTarget.parentElement.classList.add("is-active");
};

export const readMoreToggle = () => {
  document.querySelectorAll(".read-more-toggle").forEach((el) => {
    el.addEventListener("click", toggle);
  });
};
