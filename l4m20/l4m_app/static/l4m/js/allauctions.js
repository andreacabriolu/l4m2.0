function fillTables() {
    var teamPlayers = JSON.parse($('#team_players').val());

    for ([k, v] of Object.entries(teamPlayers)) {
        var newDtHtml = `<table class='table custom-table hover' id=${k}DataTable cellspacing="0">
        <caption class='table-caption'>${k}</caption>
            <thead>
                <tr class="custom-th">
                    <th>Ruolo</th>
                    <th>Giocatore</th>
                    <th>Puntata</th>
                    <th>Scaduto</th>
                    <th>Carognata</th>
                    <th>Scadenza</th>
                </tr>
            </thead>
        </table>`;


        $('#allTeamsDiv').append(newDtHtml);
        // $('table.dataTable tr td').css({ 'background-color': 'initial', 'opacity': '' });

        var dt = $(`#${k}DataTable`).DataTable(
            {
                searching: false,
                paging: false,
                info: false,
                order: [],
                createdRow: function (row, data, dataIndex) {
                    $(row).addClass(data[2] == true ? 'betting-player-expired' :
                        (data[3] == true ? 'betting-player-carognata' : 'betting-player')
                    );
                    $(row).tooltip({
                        placement: 'top',
                        animation: true,
                        title: 'SCADENZA: ' + data[5].slice(0, -6), //Bad way to remove timezone,
                        trigger: 'hover focus click',
                    });
                    if (data[1] == "VUOTO") { $(row).tooltip('disable'); }
                },
                columnDefs: [
                    {
                        target: 3,
                        visible: false
                    },
                    {
                        target: 4,
                        visible: false
                    },
                    {
                        target: 5,
                        visible: false
                    }
                ]
            },
        );

        for ([k, player_data] of Object.entries(v))
            if (player_data.id == "-1") {
                dt.row.add([
                    player_data.Role,
                    "VUOTO",
                    "",
                    "",
                    "",
                    ""
                ]).draw(false);
            }
            else {
                dt.row.add([
                    player_data.Role,
                    player_data.Surname,
                    player_data.bet__Amount,
                    player_data.bet__IsExpired,
                    player_data.bet__Carognata,
                    player_data.bet__Expiration_Date
                ]).draw(false);
            }
    }
}




window.addEventListener('DOMContentLoaded', event => {

    fillTables();

})
