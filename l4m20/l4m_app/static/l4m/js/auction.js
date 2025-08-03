let dlg, plr_dlg;
let search;
let player;
let current_div;
let officialInfo = {};

var RoleNames = {
    'P': 'PORTIERE',
    'D': 'DIFENSORE',
    'C': 'CENTROCAMPISTA',
    'A': 'ATTACCANTE',
    '': ''
};

function showPopupErrorAlert(response) {
    alert(response);
}

function showErrorAlert(response) {
    $("#error-alert").prop('hidden', false);
    $('#span-error-alert').text(response);
    $("#error-alert").fadeTo(5000, 0.33, function(){
        $("#error-alert").prop('hidden', true);
    });
}

function openPreOfficialModal(divid, playerid) {

    officialInfo = {
        'divid' : divid,
        'playerid' : playerid
    };

    $('#preOfficialModal').modal('show');
    
}

function openPlayerModal(playerName, bet=1, official=false) {
    $('#dlg_player_info').modal('show');
    $('#playerInfoLabel').text(playerName.toUpperCase());
    $('#modal-pl-info-betamount').val(bet);

    if(official) {
        $('#plr_info_modal_body').addClass('plr-info-official');
        $('#modal-currentbet').prop('hidden', true);
    }
    else {
        $('#plr_info_modal_body').removeClass('plr-info-official');
        $('#modal-currentbet').prop('hidden', false);
    }

}

function fillSlotContent(div_id, bet, expDate) {

    var htmlIsExpired = `<div>${!bet.IsOfficial ? "ASTA CONCLUSA!" : "UFFICIALE"}</div>`;
    var htmlIsNotExpired = `<input type="text" id="${div_id}_exp" class="inputFullExp" value="${expDate}" readonly>`;

    $("#" + div_id).html(`
                <div class="plr-full-r1">\
                    <input type="text" id="${div_id}_name" class="inputFullName" value="${bet.Player_id__Surname}" readonly>\
                    <input type="text" id="${div_id}_cost" class="inputFullAmount" value="${bet.Amount}">\
                </div>\
                <div class="plr-full-r2">\
                ${bet.IsExpired ?
                    htmlIsExpired :
                    htmlIsNotExpired}
                </div>\
           `);

    $('#' + div_id).addClass(`${bet.IsOfficial ? 'end-official' : ''}`);
}

function fill_slots(mbb) {
    mbb.forEach(bet => {
        div_id = bet.Slot
        expDate = bet.Expiration_Date.substr(0,19) //Format, TODO improve, I don't like it
        if (div_id != '') {
            $("#" + div_id).addClass('plr-full');
            $("#" + div_id).prop('onclick', null).off("click");
            $("#" + div_id).click(function(){
                const token = Cookies.get('csrftoken');
                var data = { 'id': bet.Player_id, 'csrfmiddlewaretoken': token };

                $.post("/l4m/auction/getPlayerInfo/", data, function (response) {
                    json_res = JSON.parse(response)
                    
                    $('#modal-pl-info-name').val(json_res.Sur);
                    $('#modal-pl-info-realteam').val(json_res.RealT);
                    $('#modal-pl-info-role').val(RoleNames[json_res.Rol]);
                    $('#modal-pl-info-betexpdate').val(json_res.BetE);
                    $('#modal-pl-info-bestbetteam').val(json_res.BetT); 
                    $('#modal-pl-info-bestbet').val(json_res.BetA);

                    if(!bet.IsExpired) {
                        openPlayerModal(json_res.Sur, json_res.BetA);
                    }
                    else if(bet.IsExpired && !bet.IsOfficial) {
                        openPreOfficialModal(div_id, bet.Player_id);
                    }
                    else if(bet.IsOfficial) {
                        openPlayerModal(json_res.Sur, json_res.BetA, official=true);
                    }
                    
                });
            });

            fillSlotContent(div_id, bet, expDate);
        }
    });
}

window.addEventListener('DOMContentLoaded', event => {
    $('#official-alert').hide();
    fill_slots(JSON.parse($('#my_best_bets').val()));

    $('.dt-content').on('click', function () {
        const player = new Object();

        player.id = $(this)[0].dataset.id;
        player.surname = $(this)[0].dataset.surname;
        player.realteam = $(this)[0].dataset.realteam;
        player.role = $(this)[0].dataset.role;
        player.betamount = $(this)[0].dataset.betamount;
        player.betexpdate = $(this)[0].dataset.betexpdate;
        player.betteam = $(this)[0].dataset.betteam;

        openPlayerDialog(player);
    });

    $('#btnplus1').on('click', function(){
        currentVal = parseInt($('#modal-pl-betamount').val());        
        currentVal = isNaN(currentVal) ? 0 : currentVal;

        $('#modal-pl-betamount').val(
            currentVal + 1
        );
    });

    $('#btnplus5').on('click', function(){
        currentVal = parseInt($('#modal-pl-betamount').val());        
        currentVal = isNaN(currentVal) ? 0 : currentVal;

        $('#modal-pl-betamount').val(
            currentVal + 5
        );
    });
})

function closeDlg(el) {
    parent = el.offsetParent;
    if(parent != null) {
        parent.close();
    }

}

function setPlayerDialog(player, mode='std') {
    if(mode == 'high') {
        $('#dlg_player_open').removeClass('dlg-player');
        $('#dlg_player_open').addClass('dlg-player-high');
        $('#notafford').attr('hidden', false);
        $('#modal-pl-betamount').val(parseInt(player.betamount));   
        $('#btnSendBet').addClass('no-pointer-events');
    }
    else {
        $('#dlg_player_open').removeClass('dlg-player-high');
        $('#dlg_player_open').addClass('dlg-player');
        $('#notafford').attr('hidden', true);
        $('#btnSendBet').removeClass('no-pointer-events');

    }
}

function openPlayerDialog(player) {

    if (!Object.is(player.name, undefined)) {
        player.name = player.name + ' '
    }
    else {
        player.name = ''
    }
    $('#modal-pl-id').val(player.id);
    $('#modal-pl-name').val(player.name + player.surname);
    $('#modal-pl-realteam').val(player.realteam);
    $('#modal-pl-role').val(RoleNames[player.role]);

    let balance_for_bets;
    const token = Cookies.get('csrftoken');
    var data = {'csrfmiddlewaretoken': token };

    $.post("/l4m/auction/getBalanceForBets/", data, function (response) {
        balance_for_bets = response;    

        if (player.betamount != 'None') {
        if(parseInt(player.betamount) >= parseInt(balance_for_bets)) { //UNAFFORDABLE
            setPlayerDialog(player, 'high');
        }
        else {
            setPlayerDialog(player);
            $('#modal-pl-betamount').val(parseInt(player.betamount) + 1);   
            $('#modal-pl-betamount').attr({"min" : parseInt(player.betamount) + 1});
        }
        }
        else {
            if(parseInt(balance_for_bets) <= 0) {
                setPlayerDialog(player, 'high');
            }
            else {
                setPlayerDialog(player);
                $('#modal-pl-betamount').val('');
                $('#modal-pl-betamount').attr({"min" : 1});
            } 
        }

        $('#modal-label-bet').html($('#modal-label-bet').html()
            .replace('_minbet_', player.betamount != 'None' ? `<strong>${parseInt(player.betamount)+1}</strong>` : '<strong>1</strong>')
            .replace('_maxbet_', `<strong>${balance_for_bets}</strong>`)
        );            
    });

    

    $('#modal-currentbet').hide();
    if (player.betexpdate != 'None') {
        $('#modal-currentbet').show();
        $('#modal-pl-bestbetteam').val(player.betteam);
        $('#modal-pl-betexpdate').val(player.betexpdate);
        $('#modal-pl-bestbet').val(player.betamount);
    }
    else {
        $('#modal-pl-bestbetteam').val('');
        $('#modal-pl-betexpdate').val('');
        $('#modal-pl-bestbet').val('');
    }

    plr_dlg = $('#dlg_player_open')[0];
    if(plr_dlg != null) 
        plr_dlg.showModal(); 
}

function openDialog(id) {
    current_div = $('#' + id + '_div');
    dlg = $('#dlg_'+id.substr(0,2)+'_open')[0];
    if (dlg!=null) 
        dlg.showModal();
}

function searchPlayer(role) {
    var filter, i, txtValue;
    search = document.getElementById('modal-ob-search_'+role);
    filter = search.value.toUpperCase();
    dl = document.getElementById("dataList_"+role);
    dt = dl.getElementsByTagName('dt');

    for (i = 0; i < dt.length; i++) {
        txtValue = dt[i].textContent;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            dt[i].style.display = "";
        } else {
            dt[i].style.display = "none";
        }
    }
}

function set_div(row) {
    current_div.addClass('plr-full');
    current_div.prop('onclick', null).off("click");
    current_div.html(`<div class="plr-full-r1">\
                            <input type="hidden" id="${current_div[0].id}_id" value="${row.playerid}">\
                            <input type="text" id="${current_div[0].id}_name" class="inputFullName" value="${row.playername}" readonly>\
                            <input type="text" id="${current_div[0].id}_cost" class="inputFullAmount" value="${row.betamount}" readonly>\
                        </div>\
                        <div class="plr-full-r2">\
                            <input type="text" id="${current_div[0].id}_exp" class="inputFullExp" value="${row.exp_date}" readonly>\
                        </div>\
    `);

    current_div.click(function(){
        const token = Cookies.get('csrftoken');
        var data = { 'id': row.playerid, 'csrfmiddlewaretoken': token };

        $.post("/l4m/auction/getPlayerInfo/", data, function (response) {
            json_res = JSON.parse(response)
            
            $('#modal-pl-info-name').val(json_res.Sur);
            $('#modal-pl-info-realteam').val(json_res.RealT);
            $('#modal-pl-info-role').val(RoleNames[json_res.Rol]);
            $('#modal-pl-info-betexpdate').val(json_res.BetE);
            $('#modal-pl-info-bestbetteam').val(json_res.BetT);
            $('#modal-pl-info-bestbet').val(json_res.BetA);

            openPlayerModal(json_res.Sur);
        });
    });
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
    return new Date(new Date(now).setDate(now.getDate() + 2)).toLocaleString("it-IT", options) //TODO nighttime
}

function sendBet() {
    const token = Cookies.get('csrftoken');
    const row = new Object();
    row.playername = $('#modal-pl-name').val();
    row.playerid = $('#modal-pl-id').val();
    row.betamount = $('#modal-pl-betamount').val();
    row.exp_date = calculate_expiration_date();
    row.userteamid = $('#user_team_id').val();
    row.userteamname = $('#user_team_name').val();
    row.balancemax = $('#my_balance_max').val();
    row.slot = current_div[0].id;
    jsonData = JSON.stringify(row);

    var data = { 'jsonData': jsonData, 'csrfmiddlewaretoken': token };

    var min = parseInt($('#modal-pl-betamount').attr("min"));
    var max = parseInt($('#modal-pl-betamount').attr("max"));

    if($('#modal-pl-betamount').attr('min') != null) {
        if(row.betamount < min) {
            showPopupErrorAlert("PUNTATA TROPPO BASSA!");
            $('#modal-pl-betamount').val(min);
            return;
        }
    }

    if($('#modal-pl-betamount').attr('max') != null) {
        if(row.betamount > max) {
            showPopupErrorAlert("PUNTATA TROPPO ALTA!");
            $('#modal-pl-betamount').val(max);
            return;
        }
    }

    $.post("/l4m/auction/sendBet/", data, function (response) {
        if(response.startsWith ('error')) {
            showErrorAlert(response);
        }
        else {
            $('#main-balance').text(`${JSON.parse(response)['amount']} / ${JSON.parse(response)['max']} FML`);
            //remove datalist entry
            entry = document.querySelector("dl.dl-class dt[data-id='"+row.playerid+"']");
            if(entry!=null) { 
                entry.parentNode.removeChild(entry); 
            }

            set_div(row);
        }
    });

    plr_dlg.close();
    dlg.close();

}

function finalizeBet() {

    div_id = officialInfo['divid'];
    pl_id = officialInfo['playerid'];
    
    const token = Cookies.get('csrftoken');
    const row = new Object();
    
    row.playername = $('#'+div_id+'_name').val();
    row.playerid = pl_id;
    row.amount = parseFloat($('#'+div_id+'_cost').val());
    row.userteamid = $('#user_team_id').val();
    
    jsonData = JSON.stringify(row);
	
	var data = { 'jsonData': jsonData, 'csrfmiddlewaretoken': token };
    $.post("/l4m/auction/finalizeBet/", data, function (response) {
        if(response.startsWith ('error')) {
        }
        else {
            $('#'+div_id).addClass('end-official');
            $('#'+div_id+'_img').prop('hidden', true);
            $('#'+div_id).children().prop('disabled', true);
            $("#official-alert").fadeTo(2000, 500);
            $("#official-alert").slideUp(500, function(){ $("#official-alert").slideUp(500); });

        }
    });
     
}
