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

    const players = JSON.parse($('#team_players').val());  // Array of player objects
    const tinfo = JSON.parse($('#team_info').val());      // Team info object

    const roleRows = {};

    // Group players by role
    for (const role of Object.keys(roleCounts)) {
        roleRows[role] = players.filter(p => p.Player__Role === role);
    }

    // Build HTML
    let html = `<div style="overflow-x: auto;width:80%;">`;

    html += `<table style="width:90%" class="table custom-table hover" id="allTeamsTable" cellspacing="0" cellpadding="5">`;

    html += `<thead><tr>`;
    html += `<th>Ruolo</th><th>Giocatore</th><th>Squadra</th><th>Costo</th><th>Durata</th><th>Ingaggio</th>`;
    html += `</tr></thead>`;
    html += `<tbody>`;

    for (const role of Object.keys(roleCounts)) {
        const label = roleLabels[role] || role;
        const count = roleCounts[role];
        const playersOfRole = roleRows[role];

        for (let i = 0; i < count; i++) {
            const player = playersOfRole[i] || {};

            // Check if player has a signed contract (Years is a valid number > 0)
            const hasContract = player.Years !== null && player.Years !== undefined && player.Years !== '' && !isNaN(player.Years);
            
            const amountText = (player.Amount !== null && player.Amount !== undefined && player.Amount !== '') 
                ? `${player.Amount} fml` 
                : '';

            const yearsText = hasContract 
                ? `${player.Years} ${Number(player.Years) === 1 ? 'anno' : 'anni'}` 
                : '';

            const salaryText = (hasContract && player.Salary !== null && player.Salary !== undefined && player.Salary !== '') 
                ? `${player.Salary} fml` 
                : '';

            const onClickAttr = player.Player__id ? `onclick="viewPlayerStats(${player.Player__id})"` : '';

            html += `<tr class="role-label ${label}-row first_column" ${onClickAttr}>`;
            if (i === 0) {
                html += `<td class="role-label ${label}-row" rowspan="${count}"><strong>${label}</strong></td>`;
            }
            html += `<td>${player.Player__Surname || '-'}</td>`;
            html += `<td>${player.Player__RealTeam__Name || ''}</td>`;
            html += `<td>${amountText}</td>`;
            html += `<td>${yearsText}</td>`;
            html += `<td>${salaryText}</td>`;
            html += `</tr>`;
        }

        // Updated colspan to 6 to match all columns
        html += `<tr class="role-separator"><td colspan="6"></td></tr>`;
    }

    html += `</tbody></table></div>`;

    $('#allTeamsDiv').html(html);
}

window.addEventListener('DOMContentLoaded', () => {
	    console.log("Script loaded and DOM ready");
        fillSingleTeamTable();
});

