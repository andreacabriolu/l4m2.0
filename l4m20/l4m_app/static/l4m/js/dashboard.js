
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

function fillSeries(c_id, series=null) {
    const token = Cookies.get('csrftoken');
    $('#select_series').empty();

    // if(series != null) {
    //     $('#select_series').val(series.Name);
    // }

    var data = { 'c_id': c_id, 'csrfmiddlewaretoken': token };

    $.post("/l4m/getSeriesByCompetition/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            var _series = JSON.parse(response);
            $.each(_series, function(idx, s) {
                $('#select_series').append($('<option>')
                .text(s[1])
                .attr('value', s[1])
                .attr('data-id', s[0]));
            });
        }
    });
}


window.addEventListener('DOMContentLoaded', event => {
    let rankingDataTable;
    const token = Cookies.get('csrftoken');
    // const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    // const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    var main_league = $('#main_league').val();
    var my_main_league_series = $('#my_main_league_series').val();
    fillSeries(main_league, series=my_main_league_series);

    $('#select_series').on('change', function(){
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
                    data: function(d) { 
                        d.c_id = $('#select_comp').children().length > 0 ? 
                            $('#select_comp').children('option:selected').data().id :
                            $('#main_league').val(), 
                        d.s_id = $('#select_series').children().length > 0 ?
                            $('#select_series').children('option:selected').data().id:
                            $('#my_main_league_series').val(),
                        d.day = $('#day').val(),
                        d.csrfmiddlewaretoken = token 
                    },
                    dataSrc: "lines",
                },
                columnDefs: [
                    {
                       className: "dt-teamname", targets: [0],
                       className: "dt-teampt", targets: [1],
                    }
                ],
                
            }
        );
    });
})