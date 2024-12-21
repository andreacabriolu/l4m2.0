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
                info: false
            }
        );

        for ([k, player_data] of Object.entries(v))
            dt.row.add([
                player_data.Surname,
                player_data.id,
            ]).draw(false);
    }
}




window.addEventListener('DOMContentLoaded', event => {

    fillTables();

})
