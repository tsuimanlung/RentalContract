/**
 * Lewis' Houses — Main JavaScript
 * Handles image preview, photo viewer, auto-dismiss alerts.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ---- Image upload preview ----
    const fileInput = document.querySelector('input[type="file"][accept*="image"]');
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (!file) return;
            const preview = document.getElementById('photoPreview');
            if (preview) {
                const reader = new FileReader();
                reader.onload = function (ev) {
                    preview.src = ev.target.result;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ---- Photo viewer modal ----
    const photoViewerImg = document.getElementById('photoViewer');
    if (photoViewerImg) {
        document.querySelectorAll('[data-bs-target="#photoViewModal"]').forEach(function (el) {
            el.addEventListener('click', function () {
                photoViewerImg.src = this.dataset.src;
                // update modal title
                const desc = this.dataset.desc || 'Photo';
                const titleEl = document.querySelector('#photoViewModal .modal-title');
                if (titleEl) titleEl.textContent = desc;
            });
        });
    }

    // ---- Auto-dismiss flash alerts after 6 seconds ----
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        var timer = setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 6000);
        // cancel timer if user hovers
        alert.addEventListener('mouseenter', function () { clearTimeout(timer); });
        alert.addEventListener('mouseleave', function () {
            timer = setTimeout(function () {
                var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }, 6000);
        });
    });

});
