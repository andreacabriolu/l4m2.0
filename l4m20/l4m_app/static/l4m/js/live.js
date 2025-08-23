
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

function buildForm(url, token, jsonData) {

        return $('<form action="' + url + '" method="post">' +
        '<input type="text" name="jsonData" value="'+jsonData+'" />' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="'+token+'" />' +
        '</form>');
    }

window.addEventListener('DOMContentLoaded', event => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    const token = Cookies.get('csrftoken');

    var cur_ser = $('#current_series').val();
    var series_to_sel = $('#select_series').children(`option[data-id=${cur_ser}]`);
    if(series_to_sel.length <= 0) { return; }
    $('#select_series').val(series_to_sel[0].value);

    $('#select_series').on('change', function () {
        var data = { 'series': $(this).children('option:selected').data().id };

        jsonData = JSON.stringify(data);
        var url = '/l4m/live/';
        form = buildForm(url, token, jsonData=data['series']);

        $('body').append(form);

        form.trigger('submit');
    });

})