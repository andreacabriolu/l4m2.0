async function apiExecute(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": Cookies.get("csrftoken")
        },
        body: JSON.stringify(data)
    });
    const json = await response.json();

    if (!response.ok) {
        throw json.error;
    }

    return json;
}

function openTeam(teamId) {
    const team = B11State.Teams.find(
        t => t.team_id === teamId
    );

    if (!team) {
        return;
    }

    B11State.SelectedTeam = team;
    renderTeamDetail(team);
}



const B11State = {
    Day: 0,
    Teams: [],
    SelectedTeam: null,
}

const B11API = {
    loadDay: async function (day) {
        const response = await fetch(`/best11/api/day/${day}/`);

        if (!response.ok) {
            throw new Error("Errore caricamento Best11");
        }

        const data = await response.json();

        B11State.Day = data.day;
        B11State.Teams = data.teams;

        renderDaySummary(data.summary);
        renderTeams(data.teams);
    }

}

const B11 = {
    init: function () {
        this.loadInitialData();
        this.bindEvents();
        this.renderDayHeader();
        this.renderSummary();
        this.renderTeams();

    },

    renderSummary: function () {


    },

    renderDayHeader: function () {
        $('#day-header').text(`Day ${B11State.Day}`);
    },

    renderTeams: function () {
        const teamContainer = $('#team-container');
        teamContainer.empty();

        // B11State.Teams.forEach(team => {
        //     const teamCard = $(`
        //         <div class="team-card">
        //             <h3>${team.name}</h3>
        //             <p>Score: ${team.score}</p>
        //         </div>
        //     `);
        //     teamContainer.append(teamCard);
        // });
    },

    loadInitialData: function () {
        var b11data = JSON.parse(document.getElementById('b11-data').textContent);

        B11State.Day = b11data.day;
        B11State.Teams = b11data.teams;
        B11State.SelectedTeam = b11data.selected_team;

    },

    bindEvents: function () {
    },
}

document.addEventListener('DOMContentLoaded', () => {
    B11.init();

});