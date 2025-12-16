
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


window.addEventListener('DOMContentLoaded', event => {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    const token = Cookies.get('csrftoken');

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
            'c_id': e.relatedTarget.dataset.comp,
            't_name': e.relatedTarget.dataset.team,
            'csrfmiddlewaretoken': token
        }

        $.post("/l4m/getTeamSeriesByCompetition/", data, function (response) {
            if (response.startsWith('error')) {
                showErrorAlert(response);
            }
            else {
                var series = JSON.parse(response);
                if (series.length <= 0) { return; }

                var _data = {
                    'teamname': e.relatedTarget.dataset.team,
                    'series': series[0],
                    'day': $('#current_day').val(),
                    'csrfmiddlewaretoken': token
                };

                $.post("/l4m/getLineupsByTeam/", _data, function (response) {
                    if (response.startsWith('error')) {
                        showErrorAlert(response);
                    }
                    else {
                        if (response == "") { return; }
                        var j_res = JSON.parse(response);
                        var l_ups = JSON.parse(j_res.l_ups);
                        var map = j_res.map;
                        add_lineups(l_ups, map);
                        $('#showLineupHistoryModalLabel').empty();
                        $('#showLineupHistoryModalLabel').append("STORICO FORMAZIONI " + e.relatedTarget.dataset.team);
                    }
                });


            }

        });
    });
});