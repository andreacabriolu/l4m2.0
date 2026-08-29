
function showErrorAlert(response) {
    $("#error-alert").prop('hidden', false);
    $('#span-error-alert').text(response);
    $("#error-alert").fadeTo(5000, 0.33, function () {
        $("#error-alert").prop('hidden', true);
    });
}

function showInfoAlert(response) {
    $("#info-alert").prop('hidden', false);
    $('#span-info-alert').text(response);
    $("#info-alert").fadeTo(5000, 0.33, function () {
        $("#info-alert").prop('hidden', true);
    });
}

window.addEventListener('DOMContentLoaded', event => {

    document.querySelectorAll('.clickable-row').forEach(function (row) {
        row.addEventListener('click', function () {
            const targetId = this.getAttribute('data-target');
            const drawerRow = document.querySelector(targetId);
            const chevron = this.querySelector('.toggle-icon');

            if (drawerRow) {
                drawerRow.classList.toggle('d-none');
                if (chevron) {
                    chevron.classList.toggle('bi-chevron-down');
                    chevron.classList.toggle('bi-chevron-up');
                }
            }
        });
    });
});




