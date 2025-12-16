
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

    return $(`<form action='${url}' method='post'><input type='text' name='jsonData' value='${jsonData}' /><input type='hidden' name='csrfmiddlewaretoken' value='${token}' /></form>`);
}

function get_pl_info(v, map) {

    ret_dict = {};

    if (map[v] != undefined) {
        ret_dict['role'] = map[v][1];
        ret_dict['surname'] = map[v][0];
        return ret_dict;
    }

    return null;
}

function add_lineups(l_ups, map) {
    var generatedTables = [];
    $('#lineups').empty();

    var _tbase = `
        <table class="l-up-table">`;

    var _tend = `</table>`;

    l_ups.forEach((l_up) => {
        var line = l_up.fields.Line;

        var _tdata = "";

        _tdata += `<thead><tr class="collapse-row"><td colspan="2">
        <button class="lup-btn btn btn-secondary" data-bs-toggle="collapse" data-bs-target="#b_${l_up.pk}">VERSIONE ${l_up.fields.Version} (${new Date(l_up.fields.Timestamp).toLocaleString("it-IT")})</button>
        </td></tr></thead>`;

        _tdata += `<tbody id="b_${l_up.pk}" class="table-group-divider collapse">`;

        _modnogk = l_up.fields.ModNoGk == true ? " (Mod No Portiere)" : "";
        _tdata += `<tr><td/><td class="mod">${line.mod}${_modnogk}</td></tr>`;

        var tits = [];
        var riss = [];

        $.each(line, function (k, v) {
            if (k.endsWith('tit')) { tits.push(v); }
            if (k.endsWith('ris')) { riss.push(v); }
        });

        $.each(tits, function (i, v) {
            cap_suffix = line.captain == v ? "[CAP]" : "";
            pl_info = get_pl_info(v, map);
            if (pl_info == null) { pl_info = { 'role': '', 'surname': 'sconosciuto' }; }
            _tdata +=
                `<tr class="lup-row">
                <td>
                    ${pl_info.role}
                </td>
                <td>
                    ${cap_suffix} ${pl_info.surname}
                </td>
            </tr>`;
        });

        _tdata += `<tr><td/><td class="sep">PANCHINA</td></tr>`;

        $.each(riss, function (i, v) {
            pl_info = get_pl_info(v, map);
            if (pl_info == null) { pl_info = { 'role': '', 'surname': 'sconosciuto' }; }
            _tdata +=
                `<tr class="lup-row">
                <td>
                    ${pl_info.role}
                </td>
                <td>
                    ${pl_info.surname}
                </td>
            </tr>`;
        });

        _tdata += `</tbody>`;

        generatedTables.push(_tbase + _tdata + _tend);

    });

    $('#lineups').append(generatedTables);
}

function fillSeries(c_id) {
    const token = Cookies.get('csrftoken');
    $('#select_series').empty();
    var all_my_series_id = $('#all_my_series_ids').val();

    var data = { 'c_id': c_id, 'csrfmiddlewaretoken': token };

    $.post("/l4m/getSeriesByCompetition/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            var _series = JSON.parse(response);
            $.each(_series, function (idx, s) {
                $('#select_series').append($('<option>')
                    .text(s[1] + (all_my_series_id.includes(s[0]) ? ' *' : ''))
                    .attr('value', s[1])
                    .attr('data-id', s[0]));
            });
        }
    }).then(
        fillDays(c_id)
    );
}

function fillDays(c_id) {
    const token = Cookies.get('csrftoken');
    $('#select_day').empty();
    var data = { 'c_id': c_id, 'csrfmiddlewaretoken': token };

    $.get("/l4m/getDaysByCompetition/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            var _days = JSON.parse(response);
            $.each(_days, function (idx, s) {
                $('#select_day').append($('<option>')
                    .text(s));
            });
        }
    });
}

window.addEventListener('DOMContentLoaded', event => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    const token = Cookies.get('csrftoken');

    var cur_comp = $('#current_competition').val();
    var comp_to_sel = $('#select_comp').children(`option[data-id=${cur_comp}]`);
    if (comp_to_sel.length <= 0) { return; }
    $('#select_comp').val(comp_to_sel[0].value);

    var cur_ser = $('#current_series').val();
    var series_to_sel = $('#select_series').children(`option[data-id=${cur_ser}]`);
    if (series_to_sel.length <= 0) { return; }
    $('#select_series').val(series_to_sel[0].value);

    var cur_day = $('#current_day').val();
    var day_to_sel = $('#select_day').children(`option[value=${cur_day}]`);
    if (day_to_sel.length <= 0) { return; }
    $('#select_day').val(day_to_sel[0].value);

    $('#b11_live_btn').on('click', function () {
        window.location.href = '/l4m/live_b11';
    });

    $('#view_live_btn').on('click', function () {
        var data = {
            'competition': $('#select_comp').children('option:selected').data().id,
            'series': $('#select_series').children('option:selected').data().id,
            'day': $('#select_day').children('option:selected').val(),
        };

        jsonData = JSON.stringify(data);
        var url = '/l4m/live/';
        form = buildForm(url, token, jsonData);

        $('body').append(form);

        form.trigger('submit');
    });

    $('#select_comp').on('change', function () {
        fillSeries($(this).children('option:selected').data().id);
    });

    $('.pl-row').on('click', function () {
        var player_id = $(this).data('pl-id');

        var data = {
            'player_id': player_id,
            'csrfmiddlewaretoken': token
        };

        $.get("/l4m/player_statistics/getBasicStats", data, function (response) {
            if (response.startsWith('error')) {
                showErrorAlert(response);
            }
            else {
                var stats = JSON.parse(response);

                $('#playerStatsModalLabel').empty();
                $('#playerStatsModalLabel').append(`STATISTICHE GIOCATORE: ${stats.name_surname}`);
                $('#modal_stats_team').empty();
                $('#modal_stats_team').append(stats.realteam);
                $('#modal_stats_role').empty();
                $('#modal_stats_role').append(stats.role);
                $('#modal_stats_games_played').empty();
                $('#modal_stats_games_played').append(stats.n_matches_played);
                $('#modal_stats_rating').empty();
                $('#modal_stats_rating').append(stats.average_vote);
                $('#modal_stats_fantamedia').empty();
                $('#modal_stats_fantamedia').append(stats.average_fantamedia);
                $('#modal_stats_goals').empty();
                $('#modal_stats_goals').append(stats.goals);
                $('#modal_stats_assists').empty();
                $('#modal_stats_assists').append(stats.assists);
                $('#modal_stats_goals_taken').empty();
                $('#modal_stats_goals_taken').append(stats.goals_conceded);
                $('#modal_stats_penalty_saved').empty();
                $('#modal_stats_penalty_saved').append(stats.penalties_saved);
                if (stats.role == 'PORTIERE') {
                    $('#modal_div_goals_taken').attr('hidden', false);
                    $('#modal_div_penalty_saved').attr('hidden', false);
                    $('#modal_div_goals').attr('hidden', true);
                    $('#modal_div_assists').attr('hidden', true);
                } else {
                    $('#modal_div_goals_taken').attr('hidden', true);
                    $('#modal_div_penalty_saved').attr('hidden', true);
                    $('#modal_div_goals').attr('hidden', false);
                    $('#modal_div_assists').attr('hidden', false);
                }
                
                $('#full_pl_stats_href').attr('href', `/l4m/player_statistics/${player_id}`);
                $('#full_pl_stats_href').text('VEDI STATISTICHE COMPLETE');

                var playerStatsModal = new bootstrap.Modal(document.getElementById('playerStatsModal'));
                playerStatsModal.show();
            }
        });
    });

    $('#showLineupHistoryModal').on('show.bs.modal', function (e) {
        const token = Cookies.get('csrftoken');

        var data = {
            'teamname': e.relatedTarget.dataset.team,
            'series': $('#current_series').val(),
            'day': $('#current_day').val(),
            'csrfmiddlewaretoken': token
        };

        $.post("/l4m/getLineupsByTeam/", data, function (response) {
            if (response.startsWith('error')) {
                showErrorAlert(response);
            }
            else {
                var j_res = JSON.parse(response);
                var l_ups = JSON.parse(j_res.l_ups);
                var map = j_res.map;
                add_lineups(l_ups, map);
                $('#showLineupHistoryModalLabel').empty();
                $('#showLineupHistoryModalLabel').append("STORICO FORMAZIONI " + e.relatedTarget.dataset.team);
            }
        });
    });

    $(function () {
        live_rankingDataTable = $('#liveRankingDataTable').DataTable(
            {
                paging: false,
                searching: false,
                ordering: false,
                layout: {
                    bottomStart: null,
                },
                order: [
                    [1, 'desc'], //Punti
                ],
                ajax: {
                    url: "/l4m/get_live_ranking/",
                    type: 'GET',
                    data: function (d) {
                        d.competition_id = $('#current_competition').val(),
                            d.series_id = $('#current_series').val(),
                            d.day = $('#current_day').val(),
                            d.all_scores = allScores,
                            d.csrfmiddlewaretoken = token
                    },
                    dataSrc: "lines",
                },
                columnDefs: [
                    { className: "dt-teamname", targets: [0] },
                    { className: "dt-teampt", targets: [1] },
                ],
                initComplete: function (settings, json) {
                    // $('#team_h_camp').removeClass('dt-teamname');
                    // $('#team_fp_h_camp').removeClass('dt-teampt');
                },
            });
    });

    $('#showLiveRankingModal').on('show.bs.modal', function (e) {
        const token = Cookies.get('csrftoken');
        $('#live_ranking_tbody').empty();

        var allScores = $('#all_scores').val();

        if (allScores=='[]') {
            var _tdata = `<tr class="lup-row"><td>ANCORA NESSUN RISULTATO LIVE DISPONIBILE</td></tr>`;
            $('#live_ranking_tbody').append(_tdata);
            return;
        }

        var data = {
            'competition_id': $('#current_competition').val(),
            'series_id': $('#current_series').val(),
            'day': $('#current_day').val(),
            'all_scores': allScores,
            'csrfmiddlewaretoken': token
        };

        $.get("/l4m/get_live_ranking/", data, function (response) {
            if (response.startsWith('error')) {
                showErrorAlert(response);
            }
            else {
                var live_ranking_items = JSON.parse(response);

                var _tdata = "";

                $.each(live_ranking_items, function (i, v) {
                    _tdata +=
                        `<tr class="lup-row">
                <td>
                    ${v[0]}
                </td>
                <td>
                    ${v[1]}
                </td>
            </tr>`;
                });

                $('#live_ranking_tbody').append(_tdata);
            }
        });




    });

});