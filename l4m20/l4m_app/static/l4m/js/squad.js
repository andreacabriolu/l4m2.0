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

    // Extract dynamic total balances from tinfo if available, defaulting to 300
    const teamData = (Array.isArray(tinfo) && tinfo.length > 0) ? tinfo[0] : (tinfo || {});
    const maxAcquisti = Math.round(Number(teamData.budget_acquisti || teamData.budget || 300));
    const maxIngaggi = Math.round(Number(teamData.budget_ingaggi || teamData.salary_budget || 300));

    const roleRows = {};
    let totalCost = 0;
    let totalSalary = 0;

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
                    .replace(/_/g, '-')
                    .replace(/\s+/g, '-');
                
                const avatarUrl = `https://static-players.fantamaster.it/resized/${cleanName}.png`;
                const defaultImg = 'https://static-players.fantamaster.it/resized/player.png';

                avatarImg = `<div class="avatar-circle"><img class="player-avatar" src="${avatarUrl}" alt="" style="width: 45px; height: 45px; object-fit: contain;" onerror="this.onerror=null; this.src='${defaultImg}';"></div>`;
            }

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

            const hasContract = player.Years !== null && player.Years !== undefined && player.Years !== '' && !isNaN(player.Years);
            
            // Safe summation
            const numAmount = Number(player.Amount);
            if (!isNaN(numAmount)) {
                totalCost += numAmount;
            }

            const numSalary = Number(player.Salary);
            const numYears = Number(player.Years);
            if (hasContract && !isNaN(numSalary) && !isNaN(numYears)) {
                totalSalary += (numSalary * numYears);
            }

            const amountText = (player.Amount !== null && player.Amount !== undefined && player.Amount !== '') 
                ? `${Math.round(player.Amount)} fml` 
                : '';

            const yearsText = hasContract 
                ? `${player.Years} ${numYears === 1 ? 'anno' : 'anni'}` 
                : '';

            const salaryText = (hasContract && player.Salary !== null && player.Salary !== undefined && player.Salary !== '') 
                ? `${Math.round(player.Salary)} fml` 
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

        html += `<tr class="role-separator"><td colspan="7"></td></tr>`;
    }

    // Convert accumulated sums to integers
    const roundedTotalCost = Math.round(totalCost);
    const roundedTotalSalary = Math.round(totalSalary);

    // Totals Row with X/300 fml format
    html += `<tr class="totals-row" style="font-weight: bold;">`;
    html += `<td colspan="4" style="text-align: right;">Spesa Monte Acquisti:</td>`;
    html += `<td>${roundedTotalCost}/${maxAcquisti} fml</td>`;
    html += `<td>Spesa Monte Ingaggi:</td>`;
    html += `<td>${roundedTotalSalary}/${maxIngaggi} fml</td>`;
    html += `</tr>`;

    html += `</tbody></table></div>`;

    $('#allTeamsDiv').html(html);
}

window.addEventListener('DOMContentLoaded', () => {
    console.log("Script loaded and DOM ready");
    fillSingleTeamTable();
});
