let dlg, plr_dlg;
let search;
let player;
let current_div;

function fill_slots(mbb) {
    mbb.forEach(bet => {
        div_id = bet.Slot
        expDate = bet.Expiration_Date.substr(0,19) //Format, TODO improve, I don't like it
        if (div_id != '') {
            $("#" + div_id).addClass('plr-full');
            $("#" + div_id).prop('onclick', null).off("click");
            $("#" + div_id).html(`<div class="plr-full-r1">\
                    <input type="text" id="${div_id}_name" class="inputFullName" value="${bet.Player_id__Surname}" readonly>\
                    <input type="text" id="${div_id}_cost" class="inputFullAmount" value="${bet.Amount}" readonly>\
                </div>\
                <div class="plr-full-r2">\
                    <input type="text" id="${div_id}_exp" class="inputFullExp" value="${expDate}" readonly>\
                </div>\
        `);
        }
    });
}

window.addEventListener('DOMContentLoaded', event => {
    fill_slots(JSON.parse($('#my_best_bets').val()));

    search = document.getElementById('modal-ob-search');

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
})

function closeDlg(el) {
    parent = el.offsetParent;
    if(parent != null) {
        parent.close();
    }

}

function openPlayerDialog(player) {
    var RoleNames = {
        'P': 'PORTIERE',
        'D': 'DIFENSORE',
        'C': 'CENTROCAMPISTA',
        'A': 'ATTACCANTE',
        '': ''
    };

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
    if (player.betamount != 'None')
        $('#modal-pl-betamount').val(parseInt(player.betamount) + 1);
    $('#modal-currentbet').hide();
    if (player.betexpdate != 'None') {
        $('#modal-currentbet').show();
        $('#modal-pl-bestbetteam').val(player.betteam);
        $('#modal-pl-betexpdate').val(player.betexpdate);
        $('#modal-pl-bestbet').val(player.betamount);
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

function searchPlayer() {
    var filter, i, txtValue;
    filter = search.value.toUpperCase();
    dl = document.getElementById("dataList");
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
                            <input type="text" id="${current_div[0].id}_name" class="inputFullName" value="${row.playername}" readonly>\
                            <input type="text" id="${current_div[0].id}_cost" class="inputFullAmount" value="${row.betamount}" readonly>\
                        </div>\
                        <div class="plr-full-r2">\
                            <input type="text" id="${current_div[0].id}_exp" class="inputFullExp" value="${row.exp_date}" readonly>\
                        </div>\
    `);
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
    return new Date(new Date(now).setDate(now.getDate() + 3)).toLocaleString("it-IT", options) //TODO nighttime
}

function sendBet() {
    const token = Cookies.get('csrftoken');
    const row = new Object()
    row.playername = $('#modal-pl-name').val();
    row.playerid = $('#modal-pl-id').val();
    row.betamount = $('#modal-pl-betamount').val();
    row.exp_date = calculate_expiration_date();
    row.userteamid = $('#user_team_id').val();
    row.userteamname = $('#user_team_name').val();
    row.slot = current_div[0].id;
    jsonData = JSON.stringify(row);

    var data = { 'jsonData': jsonData, 'csrfmiddlewaretoken': token };

    $.post("/l4m/auction/sendBet/", data, function (response) {
    });

    plr_dlg.close();
    dlg.close();

    set_div(row);
}