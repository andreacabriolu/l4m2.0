function fillSingleTableWithTeams() {
    const roleCounts = { P: 3, D: 8, C: 8, A: 6, I: 4};
    const roles = Object.keys(roleCounts);
    const teamPlayers = JSON.parse($('#team_players').val());
    const teamNames = Object.keys(teamPlayers);
    var balances = JSON.parse($('#balances').val());


    const roleRows = {};

    for (const role of roles) {
        roleRows[role] = [];
        for (let i = 0; i < roleCounts[role]; i++) {
            let row = [];
            for (const teamName of teamNames) {
                const playersOfRole = teamPlayers[teamName].filter(p => p.Role === role && p.id !== "-1");
                row.push(playersOfRole[i] ? 
                { 
					Surname: playersOfRole[i].Surname, 
					bet__Amount: playersOfRole[i].bet__Amount,
					bet__IsExpired: playersOfRole[i].bet__IsExpired,
					bet__Expiration_Date: playersOfRole[i].bet__Expiration_Date 
				} : { Surname: "", bet__Amount: "", bet__IsExpired: "", bet__Expiration_Date: "" });
                //row.push(playersOfRole[i] ? playersOfRole[i].Surname : "");
            }
            roleRows[role].push(row);
        }
    }

    // Build table
    let html = `<div style="overflow-x: auto;width:100%;">`;
    // Tgis is bad: it should load dinamically available markets and league names
    html += `<div id="link-container" style="display: flex;gap: 10px;background-color: black;padding: 10px;justify-content: center;">
      <div><a href="http://lega4mori.com/l4m/allauctions/1/" style="color: white; text-decoration: none; font-weight: bold; padding: 1px; display: block;">Serie A</a></div>                                                                        
      <div><a href="http://lega4mori.com/l4m/allauctions/2/" style="color: white; text-decoration: none; font-weight: bold; padding: 1px; display: block;">Bundesliga</a></div>                                                                        
      <div><a href="http://lega4mori.com/l4m/allauctions/3/" style="color: white; text-decoration: none; font-weight: bold; padding: 1px; display: block;">Liga</a></div>
     </div>`;
     
    html += `<table class="table custom-table hover" id="allTeamsTable" cellspacing="0" cellpadding="5">`;

    html += `<thead><tr><th>Ruolo</th>`;
    //html += `<tr class="role-separator"><td colspan="${teamNames.length + 1}"></td></tr>`;
    for (const teamName of teamNames) {
        html += `<th class="team-header fixed-width">${teamName}</th><th></th><th class="spacer-cell"></th>`;
    }
    html += `</tr></thead><tbody>`;

    for (const role of roles) {
        for (let i = 0; i < roleCounts[role]; i++) {
            html += `<tr class="role-row ${role}-row">`;
            if (i === 0) {
                html += `<td class="role-label" rowspan="${roleCounts[role]}"><strong>${role}</strong></td>`;
            }
            for (const player of roleRows[role][i]) {
                //html += `<td>${player.Surname}</td><td class="player-money">${player.bet__Amount}</td><td class="spacer-cell"></td>`;
                const color = player['bet__IsExpired'] ? 'black' : 'red';
                const date = new Date(player['bet__Expiration_Date']);
                let formatted = `${date.getHours().toString().padStart(2,'0')}:${date.getMinutes().toString().padStart(2,'0')} 
                     ${date.getDate().toString().padStart(2,'0')}-${(date.getMonth()+1).toString().padStart(2,'0')}-${date.getFullYear()}`;

                if(role == 'I') {
                    formatted = "";
                }

                html += `<td>
                  <div style="color:${color}" class="player-hover-wrapper">
                     <span class="player-name">${player.Surname}</span>
                     <span class="player-exp-date">${formatted}</span>
                 </div>
                 </td>`;
                 html += `<td style="color:${color}" class="player-money">${player.bet__Amount}</td><td class="spacer-cell"></td>`;            }
            //for (const playerName of roleRows[role][i]) {
            //    html += `<td>${playerName}</td><td class="player-money"></td>`;
            //}
            html += `</tr>`;
        }
        
        html += `<tr class="role-separator"><td colspan="${teamNames.length + 1}"></td></tr>`;
    }

    html += `</tbody></table></div>`;

    $('#allTeamsDiv').html(html);
}

window.addEventListener('DOMContentLoaded', () => {
    fillSingleTableWithTeams();
});

//function fillTables() {
//    var teamPlayers = JSON.parse($('#team_players').val());
//    var balances = JSON.parse($('#balances').val());
//
//    for ([k, v] of Object.entries(teamPlayers)) {
//        var newDtHtml = `<table class='table custom-table hover' id=${k}DataTable cellspacing="0">
//        <caption class='table-caption'>${k} [${balances[k]} FML]</caption>
//            <thead>
//                <tr class="custom-th">
//                    <th>Ruolo</th>
//                    <th>Giocatore</th>
//                    <th>Puntata</th>
//                    <th>Scaduto</th>
//                    <th>Carognata</th>
//                    <th>Scadenza</th>
//                </tr>
//            </thead>
//        </table>`;




