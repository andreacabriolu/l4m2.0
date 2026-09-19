const Best11State = {
    day: 1,
    maxDay: 35,

    teams: [],
    selectedTeam: null,

    sort: "score"
};

async function apiExecute(url, data){
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

 async function apiGetExecute(url){
    const response = await fetch(url, 
    {
        method: "GET",
        headers: {
            "Accept": "application/json"
        }
    }
    );

    const json = await response.json();

    if (!response.ok) {
        throw json.error;
    }

    return json;
}                   



const Best11 = {

    init() {
        this.renderDaySelector();
        this.bindEvents();

        this.loadDay(this.getInitialDay());
    },


    getInitialDay() {
        const element = document.querySelector(
            "[data-best11-day]"
        );

        if (!element) {
            return 1;
        }

        const day = Number(element.dataset.best11Day);

        return Number.isInteger(day)
            ? Math.max(1, Math.min(35, day))
            : 1;
    },


    bindEvents() {

        document
            .getElementById("btnPrevDay")
            ?.addEventListener(
                "click",
                () => this.changeDay(-1)
            );

        document
            .getElementById("btnNextDay")
            ?.addEventListener(
                "click",
                () => this.changeDay(1)
            );


        document
            .getElementById("best11Teams")
            ?.addEventListener(
                "click",
                event => {

                    const card =
                        event.target.closest(
                            ".best11-team-card"
                        );

                    if (!card) {
                        return;
                    }

                    const teamId =
                        Number(card.dataset.teamId);

                    this.openTeam(teamId);
                }
            );


        document
            .getElementById("best11Teams")
            ?.addEventListener(
                "keydown",
                event => {

                    if (
                        event.key !== "Enter" &&
                        event.key !== " "
                    ) {
                        return;
                    }

                    const card =
                        event.target.closest(
                            ".best11-team-card"
                        );

                    if (!card) {
                        return;
                    }

                    event.preventDefault();

                    const teamId =
                        Number(card.dataset.teamId);

                    this.openTeam(teamId);
                }
            );


        // document
        //     .getElementById("best11SortScore")
        //     ?.addEventListener(
        //         "click",
        //         () => {
        //             Best11State.sort = "score";
        //             this.renderTeams();
        //         }
        //     );
    },


    renderDaySelector() {

        const container =
            document.getElementById("best11Days");

        if (!container) {
            return;
        }

        container.innerHTML = "";

        for (let day = 1; day <= 35; day++) {

            const button =
                document.createElement("button");

            button.type = "button";
            button.className = "best11-day-btn";

            button.dataset.day = day;

            button.textContent = day;

            button.addEventListener(
                "click",
                () => this.loadDay(day)
            );

            container.appendChild(button);
        }
    },


    updateDaySelector() {

        document
            .querySelectorAll(".best11-day-btn")
            .forEach(button => {

                const day =
                    Number(button.dataset.day);

                button.classList.toggle(
                    "active",
                    day === Best11State.day
                );
            });


        const activeButton =
            document.querySelector(
                `.best11-day-btn[data-day="${Best11State.day}"]`
            );

        if (activeButton) {

            activeButton.scrollIntoView({
                behavior: "smooth",
                block: "nearest",
                inline: "center"
            });
        }


        document
            .getElementById("btnPrevDay")
            ?.toggleAttribute(
                "disabled",
                Best11State.day <= 1
            );

        document
            .getElementById("btnNextDay")
            ?.toggleAttribute(
                "disabled",
                Best11State.day >= Best11State.maxDay
            );
    },


    changeDay(delta) {

        const newDay =
            Best11State.day + delta;

        if (
            newDay < 1 ||
            newDay > Best11State.maxDay
        ) {
            return;
        }

        this.loadDay(newDay);
    },


    async loadDay(day) {

        if (
            day < 1 ||
            day > Best11State.maxDay
        ) {
            return;
        }

        Best11State.day = day;

        this.updateDaySelector();
        this.showLoading();
        this.hideError();

        try {

            const response =
                await apiGetExecute(
                    `/l4m/other/best11/day/${day}/`,
                );

            if (!response) {
                throw new Error(
                    "Nessun dato ricevuto dal server."
                );
            }

            this.applyData(response);

        } catch (error) {

            console.error(
                "Best11:",
                error
            );

            this.showError(
                "Impossibile caricare la Best11 della giornata."
            );

        } finally {

            this.hideLoading();
        }
    },


    applyData(data) {

        Best11State.day =
            Number(data.day);

        Best11State.teams =
            Array.isArray(data.teams)
                ? data.teams
                : [];

        this.renderSummary(
            data.summary ?? {}
        );

        this.renderTeams();

        this.updateDaySelector();

        // document
        //     .getElementById("currentDayLabel")
        //     .textContent =
        //     Best11State.day;

        document
            .getElementById("summaryDay")
            .textContent =
            Best11State.day;

        document
            .getElementById("teamsDay")
            .textContent =
            Best11State.day;
    },


    renderSummary(summary) {

        const section =
            document.getElementById(
                "best11Summary"
            );

        if (!section) {
            return;
        }

        const bestScore =
            Number(summary.best_score);

        const average =
            Number(summary.average_score);

        document
            .getElementById("summaryBestScore")
            .textContent =
            Number.isFinite(bestScore)
                ? bestScore.toFixed(1)
                : "-";

        const bestTeam =
            Best11State.teams.find(
                team =>
                    team.team_id ===
                    summary.best_team_id
            );

        document
            .getElementById("summaryBestTeam")
            .textContent =
            bestTeam?.team_name ?? "-";

        document
            .getElementById("summaryAverage")
            .textContent =
            Number.isFinite(average)
                ? average.toFixed(1)
                : "-";

        // document
        //     .getElementById("summaryTeams")
        //     .textContent =
        //     Best11State.teams.length;

        section.hidden = false;
    },


    renderTeams() {

        const section =
            document.getElementById(
                "best11TeamsSection"
            );

        const container =
            document.getElementById(
                "best11Teams"
            );

        if (!section || !container) {
            return;
        }

        const teams =
            [...Best11State.teams];

        if (Best11State.sort === "score") {

            teams.sort(
                (a, b) =>
                    Number(b.score) -
                    Number(a.score)
            );
        }

        container.innerHTML = "";

        teams.forEach(
            (team, index) => {

                team.rank = index + 1;

                container.appendChild(
                    this.createTeamCard(team)
                );
            }
        );

        section.hidden =
            teams.length === 0;
    },


    createTeamCard(team) {

        const card =
            document.createElement("article");

        card.className =
            "best11-team-card";

        card.dataset.teamId =
            team.team_id;

        card.tabIndex = 0;

        const score =
            Number(team.score);

        const logo =
            team.team_logo
                ? `
                    <img
                        class="best11-team-logo"
                        src="/static/l4m/images/logos/${this.escapeAttribute(team.team_logo)}"
                        alt=""
                    >
                  `
                : `
                    <div class="best11-team-logo"></div>
                  `;

        card.innerHTML = `

            <span class="best11-rank">
                ${team.rank}
            </span>

            <div class="best11-team-header">

                ${logo}

                <span class="best11-team-name">
                    ${this.escapeHtml(team.team_name)}
                </span>

            </div>

            <div class="best11-score">
                ${
                    Number.isFinite(score)
                        ? score.toFixed(1)
                        : "-"
                }

                <span class="best11-score-label">
                    FP
                </span>
            </div>

            <div class="best11-module">
                ${this.formatModule(team.module)}
            </div>

            <div class="best11-mini-field">
                ${this.renderMiniFormation(
                    team.players
                )}
            </div>

            <div class="best11-bonus-row">

                ${this.renderBonus(
                    "🛡",
                    team.modifier,
                    "+"
                )}

                ${this.renderBonus(
                    "⭐",
                    team.captain_bonus,
                    "+"
                )}

                ${this.renderBonus(
                    "✓",
                    team.all_six_bonus,
                    "+"
                )}

                ${this.renderBonus(
                    "✓",
                    team.no_yellow_bonus,
                    "+"
                )}

            </div>
        `;

        return card;
    },


    renderMiniFormation(players) {

        if (!Array.isArray(players)) {
            return "";
        }

        const starters =
            players
                .slice(0, 11)
                .sort(
                    (a, b) =>
                        Number(a.position) -
                        Number(b.position)
                );

        const lines = [
            starters.filter(p => p.role === "P"),
            starters.filter(p => p.role === "D"),
            starters.filter(p => p.role === "C"),
            starters.filter(p => p.role === "A")
        ];

        return lines
            .filter(line => line.length > 0)
            .map(
                line => `
                    <div class="best11-mini-line">
                        ${
                            line.map(
                                player => {

                                    const captain =
                                        player.captain
                                            ? " captain"
                                            : "";

                                    return `
                                        <span
                                            class="best11-mini-player${captain}"
                                            title="${this.escapeAttribute(
                                                player.surname ?? ""
                                            )}"
                                        >
                                            ${
                                                this.escapeHtml(
                                                    this.shortName(
                                                        player.surname
                                                    )
                                                )
                                            }
                                        </span>
                                    `;
                                }
                            ).join("")
                        }
                    </div>
                `
            )
            .join("");
    },


    openTeam(teamId) {

        const team =
            Best11State.teams.find(
                t =>
                    Number(t.team_id) ===
                    Number(teamId)
            );

        if (!team) {
            return;
        }

        Best11State.selectedTeam =
            team;

        this.renderTeamDetail(team);

        const modalElement =
            document.getElementById(
                "best11TeamModal"
            );

        if (!modalElement) {
            return;
        }

        const modal =
            bootstrap.Modal.getOrCreateInstance(
                modalElement
            );

        modal.show();
    },


    renderTeamDetail(team) {

        document
            .getElementById("modalDay")
            .textContent =
            Best11State.day;

        document
            .getElementById("modalTeamName")
            .textContent =
            team.team_name;

        const body =
            document.getElementById(
                "best11TeamModalBody"
            );

        const score =
            Number(team.score);

        body.innerHTML = `

            <div class="best11-detail-header">

                <div>
                    <div class="best11-detail-score">
                        ${
                            Number.isFinite(score)
                                ? score.toFixed(1)
                                : "-"
                        }
                        <span class="best11-score-label">
                            FP
                        </span>
                    </div>

                    <div class="best11-detail-module">
                        Modulo ${this.formatModule(team.module)}
                    </div>
                </div>

            </div>


            <div class="best11-field">

                ${this.renderDetailFormation(
                    team.players
                )}

            </div>


            ${this.renderBreakdown(team)}

        `;
    },


    renderDetailFormation(players) {

        if (!Array.isArray(players)) {
            return "";
        }

        const starters =
            players
                .slice(0, 11)
                .sort(
                    (a, b) =>
                        Number(a.position) -
                        Number(b.position)
                );

        const lines = [
            starters.filter(p => p.role === "P"),
            starters.filter(p => p.role === "D"),
            starters.filter(p => p.role === "C"),
            starters.filter(p => p.role === "A")
        ];

        return lines
            .filter(line => line.length)
            .map(
                line => `
                    <div class="best11-field-line">

                        ${line.map(
                            player => `
                                <div
                                    class="best11-player${
                                        player.captain
                                            ? " captain"
                                            : ""
                                    }"
                                >

                                    <div class="best11-player-dot">
                                        ${this.roleLabel(
                                            player.role
                                        )}
                                    </div>

                                    <div class="best11-player-name">
                                        ${this.escapeHtml(
                                            player.surname
                                        )}
                                    </div>

                                    <div class="best11-player-vote">
                                        ${
                                            player.totvote ??
                                            player.vote ??
                                            "-"
                                        }
                                    </div>

                                    ${
                                        player.captain
                                            ? `
                                                <span class="best11-captain-label">
                                                    ⭐ CAPITANO
                                                </span>
                                              `
                                            : ""
                                    }

                                </div>
                            `
                        ).join("")}

                    </div>
                `
            )
            .join("");
    },


    renderBreakdown(team) {

        return `

            <div class="best11-breakdown">

                <h3>
                    Dettaglio punteggio
                </h3>

                <div class="best11-breakdown-row">
                    <span>Voti giocatori</span>
                    <strong>
                        ${this.formatScore(
                            team.partial_score
                        )}
                    </strong>
                </div>

                <div class="best11-breakdown-row">
                    <span>Modificatore</span>
                    <strong>
                        ${this.formatBonus(
                            team.modifier
                        )}
                    </strong>
                </div>

                <div class="best11-breakdown-row">
                    <span>Capitano</span>
                    <strong>
                        ${this.formatBonus(
                            team.captain_bonus
                        )}
                    </strong>
                </div>

                <div class="best11-breakdown-row">
                    <span>Tutti ≥ 6</span>
                    <strong>
                        ${this.formatBonus(
                            team.all_six_bonus
                        )}
                    </strong>
                </div>

                <div class="best11-breakdown-row">
                    <span>Nessun cartellino</span>
                    <strong>
                        ${this.formatBonus(
                            team.no_yellow_bonus
                        )}
                    </strong>
                </div>

                <div class="best11-breakdown-row total">
                    <span>BEST11</span>
                    <strong>
                        ${this.formatScore(
                            team.score
                        )}
                    </strong>
                </div>

            </div>
        `;
    },


    renderBonus(icon, value, prefix = "") {

        const number =
            Number(value);

        if (
            !Number.isFinite(number) ||
            number <= 0
        ) {
            return "";
        }

        return `
            <span class="best11-bonus">
                ${icon}
                <strong>
                    ${prefix}${number.toFixed(1)}
                </strong>
            </span>
        `;
    },


    formatBonus(value) {

        const number =
            Number(value);

        if (
            !Number.isFinite(number) ||
            number === 0
        ) {
            return "—";
        }

        return number > 0
            ? `+${number.toFixed(1)}`
            : number.toFixed(1);
    },


    formatScore(value) {

        const number =
            Number(value);

        return Number.isFinite(number)
            ? number.toFixed(1)
            : "—";
    },


    formatModule(module) {

        if (!module) {
            return "—";
        }

        const value =
            String(module);

        if (value.length !== 3) {
            return value;
        }

        return `${value[0]}-${value[1]}-${value[2]}`;
    },


    roleLabel(role) {

        return {
            P: "P",
            D: "D",
            C: "C",
            A: "A"
        }[role] ?? "?";
    },


    shortName(name) {

        if (!name) {
            return "?";
        }

        const value =
            String(name);

        return value.length > 6
            ? value.slice(0, 5) + "."
            : value;
    },


    showLoading() {

        document
            .getElementById("best11Loading")
            .hidden = false;

        document
            .getElementById("best11Summary")
            .hidden = true;

        document
            .getElementById("best11TeamsSection")
            .hidden = true;
    },


    hideLoading() {

        document
            .getElementById("best11Loading")
            .hidden = true;
    },


    showError(message) {

        document
            .getElementById("best11ErrorMessage")
            .textContent =
            message;

        document
            .getElementById("best11Error")
            .hidden = false;
    },


    hideError() {

        document
            .getElementById("best11Error")
            .hidden = true;
    },


    escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent =
            value ?? "";

        return div.innerHTML;
    },


    escapeAttribute(value) {

        return this
            .escapeHtml(value)
            .replaceAll('"', "&quot;");
    }
};


document.addEventListener(
    "DOMContentLoaded",
    () => Best11.init()
);
