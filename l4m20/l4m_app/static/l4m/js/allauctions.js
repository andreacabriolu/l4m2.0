function fillTables() {
    var teamPlayers = JSON.parse($('#team_players').val());

    for ([k, v] of Object.entries(teamPlayers)) {
        var newDtHtml = `<table class='table custom-table hover' id=${k}DataTable cellspacing="0">
        <thead>
            <tr class="custom-th">
                <th>Giocatore</th>
                <th>Puntata</th>
            </tr>
        </thead>
    </table>`;

        $('#allTeamsDiv').append(newDtHtml);
        var dt = $(`#${k}DataTable`).DataTable(
            {
                searching: false,
                paging: false,
                info: false,
                order: [],
                createdRow: function (row, data, dataIndex) {
                    // if (data[1] == 'Activated') {
                        $(row).addClass('betting-player');
                    // }
                },
            
            },
        );

        for ([k, player_data] of Object.entries(v))
            if(player_data.id == "-1") {
                dt.row.add([
                    "VUOTO",
                    ""
                ]).draw(false);
            }
            else {
            dt.row.add([
                player_data.Surname,
                player_data.bet__Amount,
            ]).draw(false);}
    }
}




window.addEventListener('DOMContentLoaded', event => {

    fillTables();

})
