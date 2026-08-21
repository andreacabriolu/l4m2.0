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

    let players = [];
    let tinfo = [];

    try {
        players = JSON.parse($('#team_players').val() || '[]');
        tinfo = JSON.parse($('#team_info').val() || '[]');
    } catch (e) {
        console.error("Error parsing team data:", e);
    }

    const roleRows = {};

    // Group players by role
    for (const role of Object.keys(roleCounts)) {
        roleRows[role] = players.filter(p => p && p.Player__Role === role);
    }

    // Build HTML
    let html = `<div style="overflow-x: auto;width:80%;">`;

    html += `<table style="width:90%" class="table custom-table hover" id="allTeamsTable" cellspacing="0" cellpadding="5">`;

    html += `<thead><tr>`;
    html += `<th>Ruolo</th><th>Foto</th><th>Giocatore</th><th>Squadra</th><th>Costo</th><th>Durata</th><th>Ingaggio</th>`;
    html += `</tr></thead>`;
    html += `<tbody>`;

    for (const role of Object.keys(roleCounts)) {
        const label = roleLabels[role] || role;
        const count = roleCounts[role];
        const playersOfRole = roleRows[role] || [];

        for (let i = 0; i < count; i++) {
            const player = playersOfRole[i] || {};

            let avatarImg = '';
            if (player.Player__Surname) {
                const cleanName = String(player.Player__Surname)
                    .toLowerCase()
                    .trim()
                    .replace(/'/g, '')
                    .replace(/\s+/g, '-');
                
                const avatarUrl = `https://static-players.fantamaster.it/resized/${cleanName}.png`;
                const defaultImg = 'https://static-players.fantamaster.it/player.png';

                avatarImg = `<div class="avatar-circle"><img class="player-avatar" src="${avatarUrl}" alt="" style="width: 45px; height: 45px; object-fit: contain;" onerror="this.onerror=null; this.src='${defaultImg}';"></div>`;
            }

            // Safe team logo formatting (aligned inline without creating a new column)
            const realTeamName = player.Player__RealTeam__Name || '';
            let teamCellContent = '';

            if (realTeamName) {
                const cleanTeam = realTeamName.trim().replace(/\s+/g, '-');
                const teamLogoUrl = `https://fantamaster.b-cdn.net/teams-logos/small/${cleanTeam}.png`;

                teamCellContent = `<div class="team-cell-container">
                    <span class="team-logo-wrap">
                        <img src="${teamLogoUrl}" alt="${realTeamName}" class="team-logo-img" style="width: 45px; height: 45px; object-fit: contain;" onerror="this.onerror=null; this.style.display='none';">
                    </span>
                    <span class="team-name-text">${realTeamName}</span>
                </div>`;
            } else {
                teamCellContent = '-';
            }


            // Check if player has a signed contract (Years is a valid number)
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
            html += `<td>${avatarImg}</td>`;
            html += `<td>${player.Player__Surname || '-'}</td>`;
            html += `<td>${teamCellContent}</td>`;
            html += `<td>${amountText}</td>`;
            html += `<td>${yearsText}</td>`;
            html += `<td>${salaryText}</td>`;
            html += `</tr>`;
        }

        // Updated colspan to 7 for all columns
        html += `<tr class="role-separator"><td colspan="7"></td></tr>`;
    }

    html += `</tbody></table></div>`;

    $('#allTeamsDiv').html(html);
}
window.addEventListener('DOMContentLoaded', () => {
	    console.log("Script loaded and DOM ready");
        fillSingleTeamTable();
});

