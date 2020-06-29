// Modal container logic
// =============================================================================
export const openModal = () => {
  const modalTarget = document.querySelector("#modal-target");
  if (modalTarget) {
    modalTarget.classList.add("is-active");
  }
};

const closeModal = () => {
  const modalTarget = document.querySelector("#modal-target");
  if (modalTarget) {
    modalTarget.classList.remove("is-active");
  }
};

export const handleModalClose = () => {
  const modalBackground = document.querySelector(".modal-background");
  if (modalBackground) {
    modalBackground.addEventListener("click", () => {
      closeModal();
      // Remove HTMX inserted content
      let nextSibling;
      while ((nextSibling = modalBackground.nextElementSibling)) {
        nextSibling.remove();
      }
    });
  }
};

export const initModals = () => {
  handleModalClose();

  htmx.on("afterSwap.htmx", (e) => {
    // Activate the modal container when inserteing elements into it
    if (e.detail.target.id.includes("modal-target")) {
      openModal();
    }
  });
};
