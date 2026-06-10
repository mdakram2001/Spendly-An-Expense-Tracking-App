// main.js — students will add JavaScript here as features are built

(function () {
    // YouTube placeholder URL — replace with the real video id when ready.
    // Using youtube-nocookie.com + ?enablejsapi=1 lets us stop the video
    // by clearing the iframe src on close (the most reliable vanilla
    // approach without a YouTube IFrame API roundtrip).
    var HOW_VIDEO_SRC = "https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ?autoplay=1&rel=0&modestbranding=1&enablejsapi=1";

    function openModal(id) {
        var modal = document.getElementById(id);
        if (!modal) return;

        var iframe = modal.querySelector("iframe");
        if (iframe && !iframe.getAttribute("src")) {
            iframe.setAttribute("src", HOW_VIDEO_SRC);
        }

        modal.removeAttribute("hidden");
        document.body.style.overflow = "hidden";
    }

    function closeModal(modal) {
        if (!modal) return;
        var iframe = modal.querySelector("iframe");
        if (iframe) {
            // Clearing the src (and forcing a reload) is the most reliable
            // way to stop playback without pulling in the YouTube IFrame API.
            iframe.setAttribute("src", "");
        }
        modal.setAttribute("hidden", "");
        document.body.style.overflow = "";
    }

    // Open triggers — any element with [data-modal-open="<id>"]
    document.addEventListener("click", function (event) {
        var trigger = event.target.closest("[data-modal-open]");
        if (trigger) {
            event.preventDefault();
            openModal(trigger.getAttribute("data-modal-open"));
            return;
        }

        var closer = event.target.closest("[data-modal-close]");
        if (closer) {
            event.preventDefault();
            var modal = closer.closest(".modal");
            closeModal(modal);
        }
    });

    // Close on Escape
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            var open = document.querySelector(".modal:not([hidden])");
            if (open) closeModal(open);
        }
    });
})();
