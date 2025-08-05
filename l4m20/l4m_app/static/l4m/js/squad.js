function groupPlayersByRole(players) {
    return players.reduce((groups, player) => {
        const role = player.Player__Role || 'Unknown';
        if (!groups[role]) groups[role] = [];
        groups[role].push(player);
        return groups;
    }, {});
}

function buildTableForRole(role, players) {
    if (players.length === 0) return '';

    // Columns based on keys in player object, customize as needed
    const columns = ['Player__Role', 'Player__Surname', 'Player__RealTeam__Name', 'Jersey_num'];

    const columnHeaders = {
      'Player__Role': 'Ruolo',
      'Player__Surname': 'Player',
      'Player__RealTeam__Name': 'Squadra',
      'Jersey_num': 'Numero Maglia'
    };
    
    let html = `` //<h3>Role: ${role}</h3>`;
    html += `<table class="table custom-table hover" id="allTeamsTable" cellspacing="0" cellpadding="5">`;
    html += '<thead><tr>';
    columns.forEach(col => html += `<th>${columnHeaders[col] || col}</th>`);
    html += '</tr></thead><tbody>';

    players.forEach(player => {
        html += '<tr>';
        columns.forEach(col => {
            html += `<td>${player[col] || ''}</td>`;
        });
        html += '</tr>';
    });

    html += '</tbody></table>';
    return html;
}

function fillPlayersTable() {
    document.getElementById('team-name').textContent = teamName;

    const grouped = groupPlayersByRole(players);

    const container = document.getElementById('players-table');
    container.innerHTML = '';

    // Define roles order and names you want to show
    const roleOrder = ['P', 'D', 'C', 'A']; // e.g., P=keeper, D=defender, C=midfielder, A=forward

    roleOrder.forEach(role => {
        if (grouped[role]) {
            container.innerHTML += buildTableForRole(role, grouped[role]);
        }
    });
}

document.addEventListener('DOMContentLoaded', fillPlayersTable);

function fillSingleTableWithTeams_bla() {
    document.getElementById('team-display').textContent =
        `Keeper: ${data.keep.Player__Surname} (${data.keep.Player__RealTeam__Name})`;
}

document.addEventListener('DOMContentLoaded', fillSingleTableWithTeams);
