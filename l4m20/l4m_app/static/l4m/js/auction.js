const CANCEL_BID_TIMER = 20000; // 20 seconds

const ROLES = Object.freeze({

    P: {
        name: "PORTIERE",
        short: "P",
        icon: "bi-hand-index-thumb",
        color: "#3b82f6",
        css: "role-P"
    },

    D: {
        name: "DIFENSORE",
        short: "D",
        icon: "bi-shield",
        color: "#10b981",
        css: "role-D"
    },

    C: {
        name: "CENTROCAMPISTA",
        short: "C",
        icon: "bi-people",
        color: "#f59e0b",
        css: "role-C"
    },

    A: {
        name: "ATTACCANTE",
        short: "A",
        icon: "bi-flag",
        color: "#ef4444",
        css: "role-A"
    }

});

const ROSTER_LIMITS = Object.freeze({
    P: 3,
    D: 8,
    C: 8,
    A: 6
});

const ACTIONS = {

        bid: {
            visible: f => 
                (f.roster === false && 
                f.expired === false) ||
                (f.roster === true &&
                f.editable === true)
        },

        finalize: {
            visible: f =>
                f.roster === true && 
                f.expired === true &&
                f.official === false
        },

        contract: {
            visible: f =>
                f.roster === true &&
                f.official === true &&
                f.signed === false
        },

        free: {
            visible: f =>
                f.freeable === true
        },

        cancelBid: {
            visible: f =>
                f.editable === true
        },

        clause: {
            visible: f =>
                false //TODO: implement clause logic
        }

};

function showPopupErrorAlert(response) {
    alert(response);
}

function showErrorAlert(response) {
    $("#error-alert").prop('hidden', false);
    $('#span-error-alert').text(response);
    $("#error-alert").fadeTo(5000, 0.33, function () {
        $("#error-alert").prop('hidden', true);
    });
}

function getRemainingTime(dateString){

    if (dateString === "-" || dateString === null || dateString === undefined)
        return "-";

    const expiration = new Date(dateString.slice(0,19)); //TODO: no better way?

    const now = new Date();

    let diff = expiration - now;

    if(diff <= 0)
        return "SCADUTO";

    const minutes = Math.floor(diff/60000);

    const days = Math.floor(minutes/1440);
    const hours = Math.floor((minutes%1440)/60);
    const mins = minutes%60;

    return `${days}g ${hours}h ${mins}m`;
}

function calculate_expiration_date() {
    const now = new Date()
    let options = {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
    }
    return new Date(new Date(now).setHours(now.getHours() + AuctionState.currentSession.expiration)).toLocaleString("it-IT", options)
}

function validateMinMaxBid(newamount, min, max) {

    const btn = document.getElementById("btnBid");

    if (isNaN(newamount) || newamount < parseInt(min))
        {
            btn.classList.add("is-invalid");
            btn.disabled = true;

            document
                .getElementById("betHelp")
                .textContent =
                `Minimo: ${min} FML`;
            
                return false;

        }
        else if (isNaN(newamount) || newamount > parseInt(max))
        {
            btn.classList.add("is-invalid");
            btn.disabled = true;

            document
                .getElementById("betHelp")
                .textContent =
                `Massimo: ${max} FML`;
            
                return false;
        }
        else {

            btn.classList.remove("is-invalid");

            btn.disabled = false;

            document
                .getElementById("betHelp")
                .textContent = "";

        }

        return true;
}

function getStateClass(player){
        className = "state-bidding";

        if (player.Roster) { 
            if (player.EditableUntil) {
                className = "state-editable";
            }
            else if (!player.IsOfficial && !player.IsExpired && !player.Carognata) {
                className = "state-bidding";
            } 
        } else if (player.IsOfficial) {
            className = "state-official";
        } else if (player.IsExpired) {
            className = "state-expired";
        } else if (player.Carognata) {
            className = "state-carognata";
        }

        return className;
    
}

function buildBet(){

    return {

        playername: AuctionState.currentPlayer.Surname,
        playerid: AuctionState.currentPlayer.id,
        betamount: parseInt(
            document.querySelector("#modalBid").value
        ),
        exp_date: calculate_expiration_date(),
        userteamid: AuctionState.userTeam.id,
        userteamname: AuctionState.userTeam.name,
        balancemax: AuctionState.balance.total,
        market: AuctionState.market,
        carognata: AuctionState.currentPlayer.bet__Carognata,
        slot: 'unused',
        session: AuctionState.currentSession.id

    };

}

function validateBet(bet){

    const min = AuctionState.currentPlayer.bet__Amount;
    const max=AuctionState.balance.maxBid;
    const role = AuctionState.currentPlayer.Role;

    if(bet.amount<min){

        showPopupErrorAlert("Puntata troppo bassa");

        return false;

    }

    if(bet.amount>max){

        showPopupErrorAlert("Budget insufficiente");

        return false;

    }

    if (AuctionState.roster.filter(p => p.Player_id__Role === role).length >= ROSTER_LIMITS[role]) {

        showPopupErrorAlert("Numero massimo di giocatori per ruolo raggiunto");

        return false;

    }

    return true;

}

function buildContractData(){
    return {
        playerid: AuctionState.currentPlayer.id,
        teamid: AuctionState.userTeam.id,
        years: parseInt(document.querySelector(".contract-option.active").dataset.years)
    }

}

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

function buildFinalData(){
    return {
        playerid: AuctionState.currentPlayer.id,
        userteamid: AuctionState.userTeam.id,
        amount: AuctionState.currentPlayer.Amount,
    }

}

function buildUndoBet(undoBet){

    return {
        player_id: undoBet.playerId,
        bet_id: undoBet.betId,
    }
}

function getPlayerStatus(player, flags = null, expiration_date = null) {    

    if (flags.expired === false) {
            expired_class = "state-bidding";
            if (flags.editable === true) {
                expired_class = "state-editable";
            }
            else if (flags.carognata === true) {
                expired_class = "state-carognata";
            }

            return [getRemainingTime(expiration_date ?? player.Expiration_Date ?? "-"), 
                (expired_class)];
       }

    if (flags.roster === true &&
        flags.expired === true &&
        flags.official === false) {
            return ["SCADUTO", "state-expired"];
    }

    if (flags.roster === true &&
        flags.official === true && 
        flags.signed === false) {
        return ["UFFICIALE", "state-official"];
    }
        
    if (flags.roster === true &&
        flags.official === true &&
        flags.signed === true) {
        return ["SOTTO CONTRATTO", "state-official"]; //TODO: check signed color
    }
    
    return [getRemainingTime(expiration_date ?? player.bet__Expiration_Date ?? "-"), "state-bidding"]; //default
}

function startCountdown(undoBet) {

    timer = null

    clearInterval(timer);

    timer = setInterval(()=>{

        const remaining =
            Math.ceil((undoBet.expiresAt-Date.now())/1000);

        if(remaining<=0){

            clearInterval(timer);

            document.getElementById("btnCancelBid").hidden = true;
            // document.getElementById("btnBid").hidden = true;

            Auction.renderPlayerActions(Auction.getPlayerFlags(AuctionState.currentPlayer));

            return;

        }

        document
            .getElementById("btnCancelBid")
            .textContent =
            `Annulla puntata (${remaining} secondi)`;

    },250);

}

/* ==========================================================
 *  AUCTION API
 * ========================================================== */
const AuctionAPI = {

    async undoBet() {

        undoBet = AuctionState.undo_bets.find(b => b.playerId === AuctionState.currentPlayer.id);
        dataUndoBet = buildUndoBet(undoBet);

        try {

            const response = await apiExecute("/l4m/auction/undoBet/", dataUndoBet);
            // showPopupErrorAlert(response.message);
            AuctionState.currentPlayer.EditableUntil = null;
            AuctionState.currentPlayer.Roster = false;

            AuctionState.roster = AuctionState.roster.filter(r => r.Player_id !== AuctionState.currentPlayer.id);
            AuctionState.n_players_by_role[AuctionState.currentPlayer.Role] -= 1;
            AuctionState.players.push(AuctionState.currentPlayer);

            Auction.renderSummary();
            Auction.renderRoster();
            Auction.renderPlayers();
            Auction.refreshPlayer(AuctionState.currentPlayer);
            AuctionState.undo_bets = AuctionState.undo_bets.filter(b => b.playerId !== AuctionState.currentPlayer.id);

            bootstrap.Modal
                .getInstance(document.getElementById("playerModal"))
                ?.hide();
        }
        catch (err) {
            showPopupErrorAlert(err);
        }

    },

    async sendBet() {

        const bet = buildBet();

        if (!validateBet(bet)) {
            return;
        }

        try {

            const response = await apiExecute("/l4m/auction/sendBet/", bet);

            AuctionState.balance.maxBid = response.balance_for_bets;
            AuctionState.balance.total = response.total;
            AuctionState.balance.residual = response.residual;
            AuctionState.balance.carognate = response.n_carognate;
            AuctionState.roster = response.roster;
            AuctionState.currentPlayer.Roster = true;
            AuctionState.currentPlayer.EditableUntil = Date.now() + CANCEL_BID_TIMER;

            Auction.renderSummary();

            Auction.renderRoster();

            Auction.refreshPlayer(AuctionState.currentPlayer);

            _undoBet = {
                playerId: AuctionState.currentPlayer.id,
                betAmount: bet.betamount,
                betId: response.bet_id,
                expiresAt: Date.now() + CANCEL_BID_TIMER
            };
            AuctionState.undo_bets.push(_undoBet);

            startCountdown(_undoBet);

            Auction.removePlayerFromMarket(AuctionState.currentPlayer.id);

            bootstrap.Modal
                .getInstance(document.getElementById("playerModal"))
                ?.hide();
            

        }
        catch (err) {

            showPopupErrorAlert(err);

        }

    },

    async finalize() {

        const finalData = buildFinalData();

        try {

            const response = await apiExecute("/l4m/auction/finalizeBet/", finalData);

            player = AuctionState.getPlayer(AuctionState.currentPlayer.id);
            player.IsOfficial = true;
            player.flags = Auction.getPlayerFlags(player);

            Auction.refreshPlayer(player);

            bootstrap.Modal
                .getInstance(document.getElementById("playerModal"))
                ?.hide();

        }
        catch (err) {

            showPopupErrorAlert(err);

        }
    },

    showContractModal(){

        const modal = document.getElementById("contractModal");

        modal.querySelector(".contract-name").textContent = AuctionState.currentPlayer.Surname;

        bootstrap.Modal
            .getOrCreateInstance(modal)
            .show();
    },

    async signContract() {
        const contractData = buildContractData();

        try {

            const response = await apiExecute("/l4m/auction/signContract/", contractData);

            player = AuctionState.getPlayer(AuctionState.currentPlayer.id);
            player.squads__Years = parseInt(document.querySelector(".contract-option.active").dataset.years);

            AuctionState.balance.wages = response.wages_amount;

            Auction.refreshPlayer(player);
            Auction.renderSummary();

            bootstrap.Modal
                .getInstance(document.getElementById("contractModal"))
                ?.hide();

            bootstrap.Modal
                .getInstance(document.getElementById("playerModal"))
                ?.hide();

        }
        catch (err) {

            showPopupErrorAlert(err);

        }
    },

    freePlayer(){}

};

/* ==========================================================
 *  AUCTION STATE
 * ========================================================== */

const AuctionState = {

    currentPlayer: null,

    currentSession: {
        id: null,
        name: "",
        max_nsvincoli: 0,
        max_ncarognate: 0,
        expiration: 0
    },

    roster: [],

    market: null,

    players: [],

    balance: {
        total: 0,
        residual: 0,
        maxBid: 0,
        carognate: 0,
        wages: 0,
        wages_total: 0
    },

    filters: {
        role: "P",
        search: ""
    },

    userTeam: {
        id: null,
        name: null
    },

    n_players_by_role: {
        P: 0,
        D: 0,
        C: 0,
        A: 0
    },

    triennal_contracts_signed: {
        P: 0,
        D: 0,
        C: 0,
        A: 0
    },

    getPlayer(playerId) {
        return (
            this.roster.find(r => r.Player_id == playerId) ?? 
            this.players.find(p => p.id == playerId) ??
            null
        );
    },

    undo_bets: [],

};

const Auction = {

    updateModalFooter() {

        const footer = document.querySelector("#playerModal .modal-footer");

        const visibleButtons = [
            ...footer.querySelectorAll(".player-action")
        ].filter(button => !button.hidden);

        footer.hidden = visibleButtons.length === 0;
    },

    refreshPlayer(player){

        flags = Auction.getPlayerFlags(player);
        
        const [playerStatus, playerClass] = getPlayerStatus(player, flags);

        this.renderRosterCard(player, playerStatus, playerClass);

        this.renderPlayerModal(playerStatus);

        this.renderPlayerActions(flags);

    },

    getPlayerFlags(player) {

        return {
            roster: player.Roster ?? false,
            expired: player.IsExpired ?? false,
            official: player.IsOfficial ?? false,
            carognata: player.Carognata ?? false,
            signed: (player.squads__Years != null) ?? false,
            freeable: false, //TODO DEFINE,
            editable: (player.EditableUntil && player.EditableUntil > Date.now()) ?? false
        };
    },

    renderBidHistory(bids) {

        const container = document.getElementById("bidHistory");
        const count = document.getElementById("bidHistoryCount");
        const toggle = document.getElementById("bidHistoryToggle");

        container.innerHTML = "";
        container.hidden = true;
        count.textContent = "0";
        toggle.setAttribute(
            "aria-expanded",
            false
        );

        if (bids === undefined || bids === null) {
            return;
        }

        player_bids = bids.bids;

        count.textContent = player_bids.length;

        if (!player_bids.length) {

            container.innerHTML = `
            <div class="bid-history-empty">
                Nessun rilancio
            </div>
        `;

            return;
        }

        player_bids.forEach((bid, index) => {

            const item = document.createElement("div");

            item.className =
                "bid-history-item";
                //  + (index === 0 ? " current" : "");

            item.innerHTML = `
            <div class="bid-history-marker"></div>

            <div class="bid-history-content">

                <div class="bid-history-top">

                    <span class="bid-history-team">
                        ${bid.teamname}
                    </span>

                    <span class="bid-history-amount">
                        ${bid.amount} FML
                    </span>

                </div>

                <div class="bid-history-time">
                    ${bid.time} ${bid.carognata ?"(CAR)" : ""}
                </div>

            </div>
        `;

            container.appendChild(item);
        });
    },

    /* PLAYER CARD */
    openPlayerModal(playerId) {

        AuctionState.currentPlayer = null;

        let player = AuctionState.players.find(p =>

            p.id == playerId

        );

        if (!player) {
            player = AuctionState.roster.find(r =>
                r.Player_id == playerId
            );

            if (player) {

                //roster mapping
                player.id = player.Player_id;
                player.Roster = true;
                player.Surname = player.Player_id__Surname;
                player.RealTeam__Name = player.Player_id__RealTeam__Name;
                player.Role = player.Player_id__Role;
                player.bet__Amount = player.Amount;
                player.bet__Team_id__Name = player.Player_id__Team_id__Name; //TODO: value this?
                player.bet__Expiration_Date = player.Expiration_Date;
                player.Quotation = player.Player_id__Quotation;
            }
        }

        if (!player)
            return;

        AuctionState.currentPlayer = player;

        const flags = this.getPlayerFlags(player);
        this.renderPlayerActions(flags);

        const modal = document.getElementById("playerModal");

        modal.querySelector(".card-player-name")
            .textContent = player.Surname;

        modal.querySelector(".card-player-team")
            .textContent = player.RealTeam__Name;

        modal.querySelector(".card-player-wage")
            .textContent = "INGAGGIO: " + (Math.round(player.Quotation * 0.5) ?? "-") + " FML"; //TODO: magic number!

        role_className = `role-${player.Role}`;
        modal.querySelector(".player-role").className = `role-badge ${role_className} player-role`;

        modal.querySelector(".player-role")
            .textContent = player.Role;

        modal.querySelector(".player-current-bet")
            .textContent = player.bet__Amount ?? player.amount ?? "-";

        modal.querySelector(".player-owner")
            .textContent = player.bet__Team_id__Name ?? "-";

        expiration_date = player.bet__Expiration_Date ?? player.Expiration_Date ?? "-";
        const [playerStatus, playerClass] = getPlayerStatus(player, flags, expiration_date);
        modal.querySelector(".player-expiration")
            .textContent = playerStatus;

        const bidInput = modal.querySelector("#modalBid");

        document
                .getElementById("betHelp")
                .textContent = "";

        bidInput.min = player.bet__Amount
            ? player.bet__Amount + 1
            : 1;
        bidInput.value = bidInput.min;
        bidInput.max = AuctionState.balance.maxBid;

        bidPlusBtn = modal.querySelector("#btnPlus");
        bidMinusBtn = modal.querySelector("#btnMinus");
        bidInput.disabled = ((player.Roster && !player.EditableUntil) || player.IsExpired) ? true : false;
        bidPlusBtn.disabled = ((player.Roster && !player.EditableUntil) || player.IsExpired) ? true : false;
        bidMinusBtn.disabled = ((player.Roster && !player.EditableUntil) || player.IsExpired) ? true : false;

        document
            .getElementById("carognataAlert")
            .hidden = (player.bet__Carognata) ? false : true;

        document
            .querySelectorAll(".contract-option")
            .forEach(card => {

                card.onclick = () => {

                    document
                        .querySelectorAll(".contract-option")
                        .forEach(c => c.classList.remove("active"));

                    card.classList.add("active");

                };

            });


        const avatar = document.getElementById("player-avatar");
        avatar.src = `https://static-players.fantamaster.it/resized/${player.Surname.toLowerCase()}.png`;
        avatar.onerror = function(){
           this.src=`https://static-players.fantamaster.it/player.png`;
        }

        const bids = AuctionState.bids_history.find(b =>
            b.player_id == player.id
        );

        this.renderBidHistory(bids);

        Auction.updateModalFooter();

        bootstrap.Modal
            .getOrCreateInstance(modal)
            .show();

    },

    removePlayerFromMarket(id){

        document
            .querySelector(`.player-card[data-id="${id}"]`)
            ?.remove();

        document
            .querySelector(`.auction-market .nav-link[data-role="${AuctionState.currentPlayer.Role}"] .role-count`)
            .textContent = AuctionState.n_players_by_role[AuctionState.currentPlayer.Role] - 1;

        // AuctionState.players = AuctionState.players.filter(p => p.id != id);

    },

    renderPlayerModal(playerStatus){
    
        modal = document.getElementById("playerModal");
        modal.querySelector(".player-expiration").textContent = 
            playerStatus;
        
    },

    renderRosterCard(player, playerStatus, playerClass){
        
        player_card = document.querySelector(`.roster-card[data-id="${player.Player_id}"]`);
        if (!player_card) return;

        player_card.classList.remove(...player_card.classList);
        player_card.classList.add("roster-card", playerClass);

        player_card.querySelector(".roster-player-status").textContent = 
            playerStatus;
    
    },

    renderPlayerActions(flags){

        document
            .querySelectorAll(".player-action")
            .forEach(btn => {

                const action = ACTIONS[btn.dataset.action];

                btn.hidden = !action.visible(flags);

            });

    },

    createRosterCard(player, role){

        player.Roster = true;

        const card=document.createElement("div");

        card.className="roster-card";

        // card.classList.add(getStateClass(player));

        card.dataset.id = player.Player_id;
        card.dataset.role = role;

        const [playerStatus, playerClass] = getPlayerStatus(player, this.getPlayerFlags(player));
        card.classList.add(playerClass);

        card.innerHTML=`
            <div class="roster-player-name">${player.Player_id__Surname}</div>
            <div class="roster-player-price">$${player.Amount}</div>
            <div class="roster-player-realteam">${player.Player_id__RealTeam__Name}</div>
            <div class="roster-player-status">${playerStatus}</div>
        `;

        return card;

    },

    createEmptyCard(role) {

        const card = document.createElement("div");
        card.dataset.role = role;

        card.className = "roster-card empty";

        card.innerHTML = `
            <i class="bi bi-plus-circle"></i>
            <span>Vuoto</span>
        `;

        return card;

    },

    renderRole(role){

        const container=document.querySelector(
            `.roster-section[data-role="${role}"]`
        );

        const grid = container.querySelector(".roster-grid");
        grid.innerHTML = "";

        const roster_players=AuctionState.roster.filter(
            p=>p.Player_id__Role===role
        ).sort((a,b)=>b.Amount-a.Amount);

        container.querySelector(".roster-counter").textContent = 
            `${roster_players.length}/${ROSTER_LIMITS[role]}`;

        
        const total = ROSTER_LIMITS[role];

        for (let i = 0; i < total; i++) {

            if (i < roster_players.length) {
                grid.appendChild(this.createRosterCard(roster_players[i], role));
            } else {
                grid.appendChild(this.createEmptyCard(role));
            }
        }    

    },

    renderPlayers(searchText = "", init = false) {

        let players = AuctionState.players;

        if (AuctionState.filters.role) {

            players = players.filter(p =>
                p.Role === AuctionState.filters.role
            );

        }

        if (searchText !== "") {

            players = players.filter(p =>
                p.Surname.toLowerCase().includes(searchText)
            );

        }

        document.querySelectorAll(".player-card")
            .forEach(card => {

                const playerId = card.dataset.id;

                const isVisible = players.some(p =>
                    p.id == playerId
                );

                card.style.display = (isVisible && !init)
                    ? "block"
                    : "none";

            });
    },

    renderRoster(){

        Object.keys(ROSTER_LIMITS).forEach(role => {
            this.renderRole(role);
        });
    },

    renderSummary(){

        $("#main-residual")
            .text(AuctionState.balance.residual + "/" + AuctionState.balance.total + " FML");

        $("#main-wages")
            .text(AuctionState.balance.wages + "/" + AuctionState.balance.wages_total + " FML");

        $("#main-max_bid")
            .text(AuctionState.balance.maxBid + " FML");

        $("#main-carognate")
            .text(AuctionState.balance.carognate + "/" + AuctionState.currentSession.max_ncarognate);

    },

    onPlayerClicked(e){

        const id = e.currentTarget.dataset.id;

        AuctionState.currentPlayer = id;

        this.openPlayerModal(id);

    },

    activateRole(role){

        AuctionState.filters.role = role;

        $(".role-tabs .nav-link")
            .removeClass("active");

        $(`.role-tabs .nav-link[data-role="${role}"]`)
            .addClass("active");

        this.renderPlayers();

    },

    onRoleTabClicked(e) {

        const btn = e.target.closest(".nav-link");

        if (!btn) return;

        const role = btn.dataset.role;

        this.activateRole(role);

    },

    onRosterBidClicked(e) {

        const player_id = e.currentTarget.dataset.id;

        const roster_player = AuctionState.roster.find(r =>

            r.Player_id == player_id

        );

        if (!roster_player)
            return;

        AuctionState.currentPlayer = roster_player.Player_id;

        this.openPlayerModal(roster_player.Player_id);
    },

    onEmptySlotClicked(e) {

        const role = e.currentTarget.dataset.role;

        AuctionState.filters.role = role;

        this.activateRole(role);

        document
            .querySelector(".auction-market")
            .scrollIntoView({
                behavior: "smooth"
            });

    },

    onBidPlusClicked(e) {

        const bidInput = document.getElementById("modalBid");
        const maxBid = AuctionState.balance.maxBid;
        
        const amount = parseInt(bidInput.value);
        newAmount = amount + 1;

        if (validateMinMaxBid(newAmount, bidInput.min, maxBid)) {
            bidInput.value = newAmount;
        }
    },

    onBidMinusClicked(e) {

        const bidInput = document.getElementById("modalBid");

        const amount = parseInt(bidInput.value);
        newAmount = amount - 1;

        if (validateMinMaxBid(newAmount, bidInput.min, AuctionState.balance.maxBid)) {
            bidInput.value = newAmount;
        }

    },

    onBidInputChanged(e) {
        const amount = Number(e.target.value);

        const maxBid = AuctionState.balance.maxBid;

        validateMinMaxBid(amount, e.target.min, maxBid);
            
    },

    onPlayerCloseClicked(e) {

        const modal = document.getElementById("playerModal");

        const bootstrapModal = bootstrap.Modal.getInstance(modal);

        bootstrapModal.hide();

    },

    loadInitialData() {

        auction_data = JSON.parse(
            document.getElementById("auction_data").textContent
        );

        AuctionState.currentSession = auction_data.session;
        AuctionState.balance = auction_data.balance;
        AuctionState.roster = auction_data.roster;
        AuctionState.players = auction_data.players;
        AuctionState.market = auction_data.market;
        AuctionState.userTeam.id = auction_data.summary.user_team_id;
        AuctionState.userTeam.name = auction_data.summary.user_team_name;
        AuctionState.n_players_by_role = auction_data.summary.n_players_by_role;
        AuctionState.bids_history = auction_data.bids_history;

    },

    onSearch(e) {

        const text = e.target.value
            .trim()
            .toLowerCase();

        this.renderPlayers(text);

    },

    onExpandBidHistory(e) {

        const history = document.getElementById("bidHistory");

        const expanded =
            e.target.getAttribute("aria-expanded") === "true";

        e.target.setAttribute(
            "aria-expanded",
            String(!expanded)
        );

        history.hidden = expanded;

    },

    bindEvents() {

        $(document)
            
            .on("click", "#btnPlus",
                this.onBidPlusClicked.bind(this))

            .on("click", "#btnMinus",
                this.onBidMinusClicked.bind(this))

            .on("click", ".role-tabs",
                this.onRoleTabClicked.bind(this))

            .on("click", ".roster-card.empty",
                this.onEmptySlotClicked.bind(this))

            .on("click", ".roster-card",
                this.onRosterBidClicked.bind(this))

            .on("click", ".player-card",
                this.onPlayerClicked.bind(this))

            .on("keyup", "#player-search",
                this.onSearch.bind(this))
                
            .on("click", "#btnBid",
                AuctionAPI.sendBet.bind(AuctionAPI))
            
            .on("click", ".player-close",
                this.onPlayerCloseClicked.bind(this))

            .on("click", "#btnFinalize",
                AuctionAPI.finalize.bind(AuctionAPI))

            .on("click", "#btnContract",
                AuctionAPI.showContractModal.bind(AuctionAPI))

            .on("click", "#btnSignContract",
                AuctionAPI.signContract.bind(AuctionAPI))

            .on("input", "#modalBid", 
                this.onBidInputChanged.bind(this)) 

            .on("click", "#btnCancelBid",
                AuctionAPI.undoBet.bind(AuctionAPI))

            .on("click", "#bidHistoryToggle",
                this.onExpandBidHistory.bind(this))

            ;

    },

    init() {

        this.loadInitialData();
        this.bindEvents();

        this.renderSummary();
        this.renderRoster();
        this.renderPlayers(init=true);

    }

};

document.addEventListener("DOMContentLoaded", () => {
    Auction.init();

    // setInterval(() => {

    //     document
    //         .querySelectorAll(".player-status")
    //         .forEach(updateCountdown);

    // }, 60000);
});

