let dlg, plr_dlg;
let search;
let player;
let current_div;
let officialInfo = {};
let bet_to_free_id;

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
                f.roster === false && 
                f.expired === false
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
                f.official === true
        },

        free: {
            visible: f =>
                f.freeable === true
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

function getStateClass(player){
        className = "state-bidding";

        if (player.Roster) {
            className = "state-bidding";
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
        carognata: false, //TODO: check if this is correct
        slot: 'x',
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

function getPlayerStatus(player, flags = null) {    
    if (flags.roster === false && 
        flags.expired === false) {
            return [getRemainingTime(player.bet__Expiration_Date ?? "-"), 
                ("state-bidding" ? flags.carognata === false : "state-carognata")];
       }

    if (flags.roster === true &&
        flags.expired === true &&
        flags.official === false) {
            return ["SCADUTO", "state-expired"];
    }

    if (flags.roster === true 
        && flags.official === true && 
        flags.signed === false) {
        return ["UFFICIALE", "state-official"];
    }
        
    if (flags.roster === true &&
        flags.official === true &&
        flags.signed === true) {
        return ["SOTTO CONTRATTO", "state-official"]; //TODO: check signed color
    }
    
    return [getRemainingTime(player.bet__Expiration_Date ?? "-"), "state-bidding"]; //default
}

/* ==========================================================
 *  AUCTION API
 * ========================================================== */
const AuctionAPI = {

    async sendBet() {

        const bet = buildBet();

        if (!validateBet(bet)) {
            return;
        }

        try {

            const response = await apiExecute("/l4m/auction/sendBet/", bet);

            AuctionState.balance.maxBid = response.balance_for_bets;
            AuctionState.balance.total = response.max;
            AuctionState.balance.residual = response.amount;
            AuctionState.balance.carognate = response.n_carognate;

            AuctionState.roster = response.roster;

            Auction.renderSummary();

            Auction.renderRoster();

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

            Auction.refreshPlayer(player);

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
        wages: 0
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
    }

};

const Auction = {

    refreshPlayer(player){

        flags = Auction.getPlayerFlags(player);
        
        const [playerStatus, playerClass] = getPlayerStatus(player, flags);

        this.renderRosterCard(player, playerStatus, playerClass);

        this.renderPlayerModal(playerStatus);

        this.renderPlayerActions(player.flags);

    },

    getPlayerFlags(player) {

        return {
            roster: player.Roster ?? false,
            expired: player.IsExpired ?? false,
            official: player.IsOfficial ?? false,
            carognata: player.Carognata ?? false,
            signed: (player.squads__Years != null) ?? false,
            freeable: false, //TODO DEFINE

        };
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
            .textContent = "INGAGGIO: " + (player.Quotation ?? "-") + " FML";

        role_className = `role-${player.Role}`;
        modal.querySelector(".player-role").className = `role-badge ${role_className} player-role`;

        modal.querySelector(".player-role")
            .textContent = player.Role;

        modal.querySelector(".player-current-bet")
            .textContent = player.bet__Amount ?? "-";

        modal.querySelector(".player-owner")
            .textContent = player.bet__Team_id__Name ?? "-";

        const [playerStatus, playerClass] = getPlayerStatus(player, flags);
        modal.querySelector(".player-expiration")
            .textContent = playerStatus;

        const bidInput = modal.querySelector("#modalBid");

        bidInput.min = player.bet__Amount
            ? player.bet__Amount + 1
            : 1;
        bidInput.value = bidInput.min;
        bidInput.max = AuctionState.balance.maxBid;

        // bidInput.value = playerClass == "state-bidding" ? bidInput.min : player.bet__Amount;
        // bidInput.disabled = (playerClass != "state-bidding"); //TODO: bad practice?

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

        const card=document.createElement("div");

        card.className="roster-card";

        card.classList.add(getStateClass(player));

        card.dataset.id = player.Player_id;
        card.dataset.role = role;

        card.innerHTML=`
            <div class="roster-player-name">${player.Player_id__Surname}</div>
            <div class="roster-player-price">$${player.Amount}</div>
            <div class="roster-player-realteam">${player.Player_id__RealTeam__Name}</div>
            <div class="roster-player-status">${player.IsOfficial ? "UFFICIALE" : getRemainingTime(player.Expiration_Date ?? "-")}</div>
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
        );

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
            .text(AuctionState.balance.wages + " FML");

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

        const amount = parseInt(bidInput.value);

        if (isNaN(amount) || amount >= bidInput.max)
            return;

        bidInput.value = amount + 1;

    },

    onBidMinusClicked(e) {

        const bidInput = document.getElementById("modalBid");

        const amount = parseInt(bidInput.value);

        if (isNaN(amount) || amount <= bidInput.min)
            return;

        bidInput.value = amount - 1;

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

    },

    onSearch(e) {

        const text = e.target.value
            .trim()
            .toLowerCase();

        this.renderPlayers(text);

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



///OLD 

// function manageFreeModal() {
//     var filters = [ $('#freeGks').prop('checked') ? 'P' : 'X', 
//                     $('#freeDfs').prop('checked') ? 'D' : 'X', 
//                     $('#freeCcs').prop('checked') ? 'C' : 'X', 
//                     $('#freeFws').prop('checked') ? 'A' : 'X' ];

//     if(filters.toString() == 'X,X,X,X') { //all unchecked is all checked
//         filters = ['P','D','C','A']
//     }

//     fdl = $('#dataList_free');
//     fdt = fdl.children('dt');

//     for (i = 0; i < fdt.length; i++) {
//         if (filters.includes(fdt[i].dataset['role'])) {
//             fdt[i].style.display = "";
//         } else {
//             fdt[i].style.display = "none";
//         }
//     }

// }

// function openCarognataModal() {

//     $('#carognataModal').modal('show');

// }

// function openPreOfficialModal(divid, playerid, betamount) {

//     officialInfo = {
//         'divid': divid,
//         'playerid': playerid,
//         'betAmount': betamount
//     };

//     $('#preOfficialModal').modal('show');

// }

// function openPlayerModal(playerName, bet = 1, official = false, isFreeable = false, bet_id = null) {
//     $('#dlg_player_info').modal('show');
//     $('#playerInfoLabel').text(playerName.toUpperCase());
//     $('#modal-pl-info-betamount').val(bet);
//     bet_to_free_id = bet_id;

//     if (official) {
//         $('#plr_info_modal_body').addClass('plr-info-official');
//         $('#modal-currentbet').prop('hidden', true);

//         $('#preFreeBtn').prop('hidden', isFreeable ? false : true);

//         $('#preFreeBtn').on('click', function () {
//             $('#freeModalTitle').text(`SVINCOLARE ${playerName}?`);
//             $('#freeModal').modal('show');
//         });

//         if (isFreeable) {
//             $('#freeBtn').off();
//             $('#freeBtn').on('click', function () {
//                 const token = Cookies.get('csrftoken');

//                 var data = { 'bet_id': bet_to_free_id, 'session_svincolo': $('#current_session').val(), 'csrfmiddlewaretoken': token };

//                 $.post("/l4m/auction/freePlayer/", data, function (response) {
//                     if (response.startsWith('error')) {
//                         showPopupErrorAlert(response);
//                     }
//                     else {
//                         setTimeout(function () { window.location.reload() }, 300);
//                     }
//                 });
//             });
//         }

//     }
//     else {
//         $('#plr_info_modal_body').removeClass('plr-info-official');
//         $('#modal-currentbet').prop('hidden', false);
//     }

// }

// function fillSlotContent(div_id, bet, expDate) {

//     var htmlIsExpired = `<div>${!bet.IsOfficial ? "ASTA CONCLUSA!" : "UFFICIALE"}</div>`;
//     var htmlIsNotExpired = `<input type="text" id="${div_id}_exp" class="inputFullExp" value="${expDate}" readonly>`;

//     $("#" + div_id).html(`
//                 <div class="plr-full-r1">\
//                     <input type="text" id="${div_id}_name" class="inputFullName" value="${bet.Player_id__Surname}" readonly>\
//                     <input type="text" id="${div_id}_cost" class="inputFullAmount" value="${bet.Amount}">\
//                 </div>\
//                 <div class="plr-full-r2">\
//                 ${bet.IsExpired ?
//             htmlIsExpired :
//             htmlIsNotExpired}
//                 </div>\
//            `);

//     $('#' + div_id).addClass(`${bet.Carognata ? 'carognata' : ''}`);
//     $('#' + div_id).addClass(`${bet.IsExpired && !bet.IsOfficial ? 'end-expired' : ''}`);
//     $('#' + div_id).addClass(`${bet.IsOfficial ? 'end-official' : ''}`);

// }

// function checkPlayerFreeable(json_res) {
//     return (
//         !(json_res.IsActive) ||
//         json_res.BetSessionId != $('#current_session').val()
//     );
// }

// function fill_slots(mbb) {
//     mbb.forEach(bet => {
//         div_id = bet.Slot
//         expDate = new Date(bet.Expiration_Date).toLocaleString("it-IT", { timeZone: "UTC" })
//         if (div_id != '') {
//             $("#" + div_id).addClass('plr-full');
//             $("#" + div_id).prop('onclick', null).off("click");
//             $("#" + div_id).click(function () {
//                 const token = Cookies.get('csrftoken');
//                 var data = { 'id': bet.Player_id, 'csrfmiddlewaretoken': token };

//                 $.post("/l4m/auction/getPlayerInfo/", data, function (response) {
//                     json_res = JSON.parse(response)

//                     $('#modal-pl-info-name').val(json_res.Sur);
//                     $('#modal-pl-info-realteam').val(json_res.RealT);
//                     $('#modal-pl-info-role').val(RoleNames[json_res.Rol]);
//                     $('#modal-pl-info-betexpdate').val(new Date(json_res.BetE).toLocaleString("it-IT", { timeZone: "UTC" }));
//                     $('#modal-pl-info-bestbetteam').val(json_res.BetT);
//                     $('#modal-pl-info-bestbet').val(json_res.BetA);
//                     //TODO: player can NOT be free if it is bought in this market session!
//                     isFreeable = checkPlayerFreeable(json_res);

//                     if (!bet.IsExpired) {
//                         openPlayerModal(json_res.Sur, json_res.BetA);
//                     }
//                     else if (bet.IsExpired && !bet.IsOfficial) {
//                         openPreOfficialModal(div_id, bet.Player_id, json_res.BetA);
//                     }
//                     else if (bet.IsOfficial) {
//                         openPlayerModal(json_res.Sur, json_res.BetA, official = true, freeable = isFreeable, json_res.BetId);
//                     }

//                 });
//             });

//             fillSlotContent(div_id, bet, expDate);
//         }
//     });
// }

// window.addEventListener('DOMContentLoaded', event => {
//     const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
//     const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

//     $('#official-alert').hide();
//     fill_slots(JSON.parse($('#my_best_bets').val()));

//     $('.dt-content').on('click', function () {
//         const player = new Object();

//         player.id = $(this)[0].dataset.id;
//         player.surname = $(this)[0].dataset.surname;
//         player.realteam = $(this)[0].dataset.realteam;
//         player.role = $(this)[0].dataset.role;
//         player.betamount = $(this)[0].dataset.betamount;
//         player.betexpdate = $(this)[0].dataset.betexpdate;
//         player.betteam = $(this)[0].dataset.betteam;
//         player.carognata = $(this)[0].dataset.carognata;

//         openPlayerDialog(player);
//     });

//     $('#btnplus1').on('click', function () {
//         currentVal = parseInt($('#modal-pl-betamount').val());
//         currentVal = isNaN(currentVal) ? 0 : currentVal;

//         $('#modal-pl-betamount').val(
//             currentVal + 1
//         );
//     });

//     $('#btnplus5').on('click', function () {
//         currentVal = parseInt($('#modal-pl-betamount').val());
//         currentVal = isNaN(currentVal) ? 0 : currentVal;

//         $('#modal-pl-betamount').val(
//             currentVal + 5
//         );
//     });

//     $('#freeGks,#freeDfs,#freeCcs,#freeFws').on('change', function() {
//         manageFreeModal();
//     });

//     if($('#current_session').val() == "") {
//         $('#main-div-container').addClass('no-pointer-events-opaque');
//     }
//     else {
//         $('#main-div-container').removeClass('no-pointer-events-opaque');
//     }
// })

// function closeDlg(el) {
//     parent = el.offsetParent;
//     if (parent != null) {
//         parent.close();
//     }

// }

// function setPlayerDialog(player, mode = 'std') {
//     if (mode == 'high') {
//         $('#dlg_player_open').removeClass('dlg-player');
//         $('#dlg_player_open').addClass('dlg-player-high');
//         $('#notafford').attr('hidden', false);
//         $('#modal-pl-betamount').val(parseInt(player.betamount) + 1);
//         $('#modal-pl-betamount').attr({ "min": parseInt(player.betamount) });
//         $('#modal-pl-betamount').prop('disabled', true);
//         $('#btnSendBet').addClass('no-pointer-events');
//     }
//     else {
//         $('#dlg_player_open').removeClass('dlg-player-high');
//         $('#dlg_player_open').addClass('dlg-player');
//         $('#notafford').attr('hidden', true);
//         $('#btnSendBet').removeClass('no-pointer-events');
//         $('#modal-pl-betamount').prop('disabled', false);
//     }

//     if (mode == "carognata") {
//         $('#dlg_player_open').removeClass('dlg-player');
//         $('#dlg_player_open').addClass('dlg-player-carognata');
//         // $('#carognata_span').attr('hidden', false);
//     }
//     else {
//         $('#dlg_player_open').removeClass('dlg-player-carognata');
//         $('#dlg_player_open').addClass('dlg-player');
//         // $('#span-betexpire').html("Scadenza");
//         // $('#carognata_span').attr('hidden', true);

//     }

// }

// function set_bet_min_max(betamount, maxbet) {
//     let baseStr = 'PUNTATA (MIN: _minbet_ MAX: _maxbet_)';

//     $('#modal-label-bet').html(baseStr
//         .replace('_minbet_', betamount != 'None' ? `<strong>${parseInt(betamount) + 1}</strong>` : '<strong>1</strong>')
//         .replace('_maxbet_', `<strong>${maxbet}</strong>`)
//     );
// }

// function openPlayerDialog(player) {

//     if (!Object.is(player.name, undefined)) {
//         player.name = player.name + ' '
//     }
//     else {
//         player.name = ''
//     }
//     $('#modal-pl-id').val(player.id);
//     $('#modal-pl-name').val(player.name + player.surname);
//     $('#modal-pl-realteam').val(player.realteam);
//     $('#modal-pl-role').val(RoleNames[player.role]);

//     let balance_for_bets;
//     const token = Cookies.get('csrftoken');
//     var data = { 'csrfmiddlewaretoken': token };

//     $.post("/l4m/auction/getBalanceForBets/", data, function (response) {
//         balance_for_bets = response;

//         if (player.betamount != 'None') {
//             if (parseInt(player.betamount) >= parseInt(balance_for_bets)) { //UNAFFORDABLE
//                 setPlayerDialog(player, 'high');
//             }
//             else {
//                 setPlayerDialog(player);
//                 $('#modal-pl-betamount').val(parseInt(player.betamount) + 1);
//                 $('#modal-pl-betamount').attr({ "min": parseInt(player.betamount) + 1 });
//             }
//         }
//         else {
//             if (parseInt(balance_for_bets) <= 0) {
//                 setPlayerDialog(player, 'high');
//             }
//             else {
//                 setPlayerDialog(player);
//                 $('#modal-pl-betamount').val(1);
//                 $('#modal-pl-betamount').attr({ "min": 1 });
//             }
//         }

//         if (player.carognata == "True") {
//             setPlayerDialog(player, "carognata");
//             // $('#span-betexpire').html(span-betexpire.text() + " (CAROGNATA) ");
//         }
//         else {
//             setPlayerDialog(player);
//         }

//         set_bet_min_max(player.betamount, balance_for_bets);

//     });



//     $('#modal-currentbet').hide();
//     if (player.betexpdate != 'None') {
//         $('#modal-currentbet').show();
//         $('#modal-pl-bestbetteam').val(player.betteam);
//         $('#modal-pl-betexpdate').val(new Date(player.betexpdate).toLocaleString("it-IT", { timeZone: "UTC" }));
//         $('#modal-pl-bestbet').val(player.betamount);
//         $('#modal-pl-carognata').val(player.carognata);
//     }
//     else {
//         $('#modal-pl-bestbetteam').val('');
//         $('#modal-pl-betexpdate').val('');
//         $('#modal-pl-bestbet').val('');
//         $('#modal-pl-carognata').val('');
//     }

//     plr_dlg = $('#dlg_player_open')[0];
//     if (plr_dlg != null)
//         plr_dlg.showModal();
// }

// function openDialog(id) {
//     current_div = $('#' + id + '_div');
//     dlg = $('#dlg_' + id.substr(0, 2) + '_open')[0];
//     if (dlg != null)
//         dlg.showModal();
// }

// function searchPlayer(role) {
//     var filter, i, txtValue;
//     search = document.getElementById('modal-ob-search_' + role);
//     filter = search.value.toUpperCase();
//     dl = document.getElementById("dataList_" + role);
//     dt = dl.getElementsByTagName('dt');

//     for (i = 0; i < dt.length; i++) {
//         txtValue = dt[i].textContent;
//         if (txtValue.toUpperCase().indexOf(filter) > -1) {
//             dt[i].style.display = "";
//         } else {
//             dt[i].style.display = "none";
//         }
//     }
// }

// function set_div(row) {
//     current_div.addClass('plr-full');
//     current_div.prop('onclick', null).off("click");
//     current_div.html(`<div class="plr-full-r1">\
//                             <input type="hidden" id="${current_div[0].id}_id" value="${row.playerid}">\
//                             <input type="text" id="${current_div[0].id}_name" class="inputFullName" value="${row.playername}" readonly>\
//                             <input type="text" id="${current_div[0].id}_cost" class="inputFullAmount" value="${row.betamount}" readonly>\
//                         </div>\
//                         <div class="plr-full-r2">\
//                             <input type="text" id="${current_div[0].id}_exp" class="inputFullExp" value="${row.exp_date}" readonly>\
//                         </div>\
//     `);

//     current_div.click(function () {
//         const token = Cookies.get('csrftoken');
//         var data = { 'id': row.playerid, 'csrfmiddlewaretoken': token };

//         $.post("/l4m/auction/getPlayerInfo/", data, function (response) {
//             json_res = JSON.parse(response)

//             $('#modal-pl-info-name').val(json_res.Sur);
//             $('#modal-pl-info-realteam').val(json_res.RealT);
//             $('#modal-pl-info-role').val(RoleNames[json_res.Rol]);
//             $('#modal-pl-info-betexpdate').val(json_res.BetE);
//             $('#modal-pl-info-bestbetteam').val(json_res.BetT);
//             $('#modal-pl-info-bestbet').val(json_res.BetA);

//             openPlayerModal(json_res.Sur);
//         });
//     });
// }



// function sendBet() {
//     const token = Cookies.get('csrftoken');
//     const row = new Object();
//     row.playername = $('#modal-pl-name').val();
//     row.playerid = $('#modal-pl-id').val();
//     row.betamount = $('#modal-pl-betamount').val();
//     row.exp_date = calculate_expiration_date();
//     row.userteamid = $('#user_team_id').val();
//     row.userteamname = $('#user_team_name').val();
//     row.balancemax = $('#my_balance_max').val();
//     row.market = $('#my_market').val();
//     row.carognata = $('#modal-pl-carognata').val();
//     row.slot = current_div[0].id;
//     row.session = $('#current_session').val();
//     jsonData = JSON.stringify(row);

//     var data = { 'jsonData': jsonData, 'csrfmiddlewaretoken': token };

//     var min = parseInt($('#modal-pl-betamount').attr("min"));
//     var max = parseInt($('#modal-pl-betamount').attr("max"));

//     if ($('#modal-pl-betamount').attr('min') != null) {
//         if (row.betamount < min) {
//             showPopupErrorAlert("PUNTATA TROPPO BASSA!");
//             $('#modal-pl-betamount').val(min);
//             return;
//         }
//     }

//     if ($('#modal-pl-betamount').attr('max') != null) {
//         if (row.betamount > max) {
//             showPopupErrorAlert("PUNTATA TROPPO ALTA!");
//             $('#modal-pl-betamount').val(max);
//             return;
//         }
//     }

//     if ($('#modal-pl-carognata').val() == "True") {
//         showPopupErrorAlert("RILANCIO CAROGNA!");
//     }

//     $.post("/l4m/auction/sendBet/", data, function (response) {
//         if (response.startsWith('error')) {
//             showPopupErrorAlert(response);
//         }
//         else {
//             $('#main-balance').text(`${JSON.parse(response)['max']} FML`);
//             $('#main-carognate').text(`${JSON.parse(response)['n_carognate']} / 3`);
//             new_residual = parseInt(JSON.parse(response)['amount']);
//             $('#main-residual').text(`${new_residual} FML`);
//             set_bet_min_max(null, JSON.parse(response)['amount'])
//             entry = document.querySelector("dl.dl-class dt[data-id='" + row.playerid + "']");
//             if (entry != null) {
//                 entry.parentNode.removeChild(entry);
//             }

//             set_div(row);
//         }
//     });

//     plr_dlg.close();
//     dlg.close();

// }

// function finalizeBet() {

//     div_id = officialInfo['divid'];
//     pl_id = officialInfo['playerid'];
//     pl_amount = officialInfo['betAmount'];

//     const token = Cookies.get('csrftoken');
//     const row = new Object();

//     row.playerid = pl_id;
//     row.amount = parseInt(pl_amount);
//     row.userteamid = $('#user_team_id').val();

//     jsonData = JSON.stringify(row);

//     var data = { 'jsonData': jsonData, 'csrfmiddlewaretoken': token };
//     $.post("/l4m/auction/finalizeBet/", data, function (response) {
//         if (response.startsWith('error')) {
//             showPopupErrorAlert(response);
//         }
//         else {
//             $('#' + div_id).addClass('end-official');
//             $('#' + div_id + '_img').prop('hidden', true);
//             $('#' + div_id).children().prop('disabled', true);
//             $("#official-alert").fadeTo(2000, 500);
//             $("#official-alert").slideUp(500, function () { $("#official-alert").slideUp(500); });

//         }
//     });

// }
