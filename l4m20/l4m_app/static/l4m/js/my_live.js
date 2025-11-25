
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
        <button class="lup-btn btn btn-secondary" data-bs-toggle="collapse" data-bs-target="#b_${l_up.pk}">VERSIONE ${l_up.fields.Version} (${new Date(l_up.fields.Timestamp).toLocaleString("it-IT", { timeZone: "UTC" })})</button>
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


})