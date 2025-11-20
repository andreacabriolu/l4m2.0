function showPopupErrorAlert(response) {
    alert(response);
}
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
            var days = [...Array(parseInt(response) + 1).keys()].slice(1);
            $.each(days, function (idx, day) {
                $('#select_day').append($('<option>')
                    .text(day)
                    .attr('value', day));
            });
            $('#select_day').children(`option[value=${days[parseInt(response) - 1]}]`).prop('selected', true);
        }
    });
}

function calculate(c_id, d_id, allcomp = true) {
    const token = Cookies.get('csrftoken');

    var data = { 'competitionid': c_id, 'all_comp': $('#allCompChk').prop('checked'), 'day': parseInt(d_id), 'csrfmiddlewaretoken': token };

    $('#spinner').attr('hidden', false);
    $.post("/l4m/calculate/calculateDay/", data, function (response) {
        if (response.startsWith('error')) {
            $('#spinner').attr('hidden', true);
            showPopupErrorAlert(response);
        }
        else {
            $('#spinner').attr('hidden', true);
            showPopupErrorAlert(response);
            if (allcomp) {
                advanceDay(nopopup = true); //calculate AND advance
            }
        }
    });

}

function set_day(day, nopopup = false) {
    const token = Cookies.get('csrftoken');

    var data = { 'day': parseInt(day), 'csrfmiddlewaretoken': token };

    $.post("/l4m/calculate/setDay/", data, function (response) {
        if (response.startsWith('error')) {
            showPopupErrorAlert(response);
        }
        else {
            $('#cur-day-val').val(response);
            if (!nopopup) {
                $('#modal-text').text('GIORNATA AVANZATA O IMPOSTATA');
                $('#confirmModal').modal('show');
            }
        }
    });
}

function advanceDay(nopopup = false) {
    var cur_day_val = $('#cur-day-val').val();
    set_day(parseInt(cur_day_val) + 1, nopopup);
}

function showMissingLups(teamid, teamname) {

    $('#missingLupModal_title').text(teamname);
    var cur_day_val = $('#cur-day-val').val();

    const token = Cookies.get('csrftoken');

    var data = { 't_id': teamid, 'day': cur_day_val, 'csrfmiddlewaretoken': token };

    $.get("/l4m/calculate/getMissingLineups/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            $('#missingLupModal .modal-body').empty();
            lups = JSON.parse(response);

            lups.filled_comps_names.forEach(lup => 
                {
                var chk = `<div class="form-check">
                            <input class="form-check-input" type="checkbox" checked>
                            <label class="form-check-label">
                                ${lup}
                            </label>
                            </div>`;

                $('#missingLupModal .modal-body').append(chk);
            });

            lups.missing_comps_names.forEach(lup => 
                {
                var chk = `<div class="form-check">
                            <input class="form-check-input" type="checkbox">
                            <label class="form-check-label">
                                ${lup}
                            </label>
                            </div>`;

                $('#missingLupModal .modal-body').append(chk);
            });
        }
    });



    $('#missingLupModal').modal('show');

}

window.addEventListener('DOMContentLoaded', event => {
    c_id = $('#select_comp').children('option:selected').data().id;
    fill_days(c_id);

    $('#allCompChk').on('change', function () {
        $('#select_comp').prop('disabled', $(this).prop('checked'));
    });

    $('#btnCalculate').on('click', function () {
        d_id = $('#select_day').children('option:selected').val();
        c_id = $('#select_comp').children('option:selected').data().id;
        allcomp = $('#allCompChk').prop('checked');
        calculate(c_id, d_id, allcomp);
    });

    $('#btnAdvanceDay').on('click', function () {
        advanceDay();
    });

    $('#btnSetDay').on('click', function () {
        var cur_day_val = $('#cur-day-val').val();
        set_day(cur_day_val);
    });

    $('#customDayChk').on('click', function () {
        if ($(this).prop('checked')) {
            $('#btnAdvanceDay').prop('disabled', true);
            $('#cur-day-val').prop('readonly', false);
            $('#btnSetDay').prop('disabled', false);
        }
        else {
            $('#btnAdvanceDay').prop('disabled', false);
            $('#cur-day-val').prop('readonly', true);
            $('#btnSetDay').prop('disabled', true);
        }
    });

})