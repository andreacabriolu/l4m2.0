
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

function fill_days(c_id) {
    const token = Cookies.get('csrftoken');

    $('#select_day').empty();

    var data = { 'competitionid': c_id, 'csrfmiddlewaretoken': token };

    $.post("/l4m/calculate/getCurrentDayByCompetition/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            var days = [...Array(parseInt(response)+1).keys()].slice(1);
            $.each(days, function(idx, day) {
                $('#select_day').append($('<option>')
                .text(day)
                .attr('value', day));
            });
        }
    });
}

function calculate(c_id, d_id) {
    const token = Cookies.get('csrftoken');

    var data = { 'competitionid': c_id, 'day': parseInt(d_id), 'csrfmiddlewaretoken': token };

    $.post("/l4m/calculate/calculateDay/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            
        }
    });

}


window.addEventListener('DOMContentLoaded', event => {
    c_id = $(select_comp).children('option:selected').data().id;
    fill_days(c_id);

    $('#select_comp').on('change', function () {
        c_id = $(this).children('option:selected').data().id;
        fill_days(c_id);

    });

    $('#btnCalculate').on('click', function() {
        d_id = $('#select_day').children('option:selected').val();
        calculate(c_id, d_id);
    });

})