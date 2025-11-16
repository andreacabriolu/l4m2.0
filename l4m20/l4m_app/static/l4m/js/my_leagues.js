
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
    let rankingDataTable;
    const token = Cookies.get('csrftoken');
    // const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    // const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    var comp_id = $('#comp').val();
    // var my_main_league_series = $('#my_main_league_series').val();
    // fillSeries(main_league);

    $('#select_series').on('change', function () {
        rankingDataTable.ajax.reload();
    });

     $('#view_live_btn').on('click', function() {
        rankingDataTable.ajax.reload();
    });

    $(function () {
        rankingDataTable = $('#rankingDataTable').DataTable(
            {
                paging: false,
                searching: false,
                layout: {
                    bottomStart: null,
                },
                order: [
                    [1, 'desc'], //Punti
                    [2, 'desc'] //Fantapunti
                ],
                ajax: {
                    url: "/l4m/retrieveRankingInfo/",
                    type: 'POST',
                    data: function (d) {
                        d.c_id = comp_id,
                        d.s_id = $('#select_series').children('option:selected').data().id,
                        d.day = $('#day').val(),
                        d.csrfmiddlewaretoken = token
                    },
                    dataSrc: "lines",
                },
                columnDefs: [
                    { className: "dt-teamname", targets: [0] },
                    { className: "dt-teampt", targets: [1] },
                ],
                initComplete: function (settings, json) {
                    $('#team_h_camp').removeClass('dt-teamname');
                    $('#team_fp_h_camp').removeClass('dt-teampt');
                },
            }
        );
    });
});