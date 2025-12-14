function groupPlayersByRole(players) {
    return players.reduce((groups, player) => {
        const role = player.Player__Role || 'Unknown';
        if (!groups[role]) groups[role] = [];
        groups[role].push(player);
        return groups;
    }, {});
}

function viewPlayerStats(player_id) {
    const url = `/l4m/player_statistics/${player_id}/`;
    window.location.href = url;
}

function fillSingleTeamTable() {
    const roleCounts = { P: 3, D: 8, C: 8, A: 6 };
    const roleLabels = { P: 'P', D: 'D', C: 'C', A: 'A' };

    const players = JSON.parse($('#team_players').val());  // This should be an array of player objects
    const tinfo = JSON.parse($('#team_info').val());  // This should be an array of player objects

    const roleRows = {};

     // Group players by role
    for (const role of Object.keys(roleCounts)) {
     roleRows[role] = players.filter(p => p.Player__Role === role);
    }


    // Build HTML
    let html = `<div style="overflow-x: auto;width:80%;">`;

    html += `<table  style="width:90%"  class="table custom-table hover" id="allTeamsTable" cellspacing="0" cellpadding="5">`;

    html += `<tbody><tr>`;
    html += `<th>Ruolo</th><th>Giocatore</th><th>Squadra</th><th>Costo</th>`;
    html += `</tr></tbody>`;
    html += `<tbody>`;

    for (const role of Object.keys(roleCounts)) {
        const label = roleLabels[role] || role;
        const count = roleCounts[role];
        const playersOfRole = roleRows[role];

        for (let i = 0; i < count; i++) {
            const player = playersOfRole[i] || {};

            html += `<tr class="role-label ${label}-row first_column" onclick="viewPlayerStats(${player.Player__id})">`;
            if (i === 0) {
                html += `<td class="role-label ${label}-row" rowspan="${count}"><strong>${label}</strong></td>`;
            }
            html += `<td>${player.Player__Surname || '-'}</td>`;
            html += `<td>${player.Player__RealTeam__Name || ''}</td>`;
            html += `<td>${player.Amount || ''}</td>`;
            html += `</tr>`;
        }

        html += `<tr class="role-separator"><td colspan="4"></td></tr>`;
    }

    html += `</tbody></table></div>`;

    $('#allTeamsDiv').html(html);
}

window.addEventListener('DOMContentLoaded', () => {
	    console.log("Script loaded and DOM ready");
        fillSingleTeamTable();
});

