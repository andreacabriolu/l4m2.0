let dlg;
let search;
let player;
let current_div;

window.addEventListener('DOMContentLoaded', event => {

    dlg = document.getElementById('dlg open');
    plr_dlg = document.getElementById('dlg_player open');
    search = document.getElementById('modal-ob-search');

    gkdivs = document.getElementsByClassName('gk-div');
    gkcont = document.getElementById('gks');

    gkcont.addEventListener("click", function (e) {
        openDialog(e['target'].id);
    })

    var closeMain = document.getElementById("closeMain");
    var closePlayer = document.getElementById("closePlayer");
    closeMain.addEventListener("click", function () {
        dlg.close();
        search.value = '';
    })

    closePlayer.addEventListener("click", function () {
        plr_dlg.close();
        search.value = '';
    })

    $('.dt-content').on('click', function () {
        const player = new Object();

        player.id = $(this)[0].dataset.id;
        player.surname = $(this)[0].dataset.surname;
        player.realteam = $(this)[0].dataset.realteam;
        player.role = $(this)[0].dataset.role;

        openPlayerDialog(player);
    });

    $('#span-betexpire').hide();
    $('#modal-pl-bettime').hide();

})

function openPlayerDialog(player) {
    var RoleNames = {
         'P':'PORTIERE', 
         'D':'DIFENSORE',
         'C':'CENTROCAMPISTA',
         'A':'ATTACCANTE',
         '': ''};

    $('#modal-pl-id').val(player.id);
    $('#modal-pl-name').val(player.surname);
    $('#modal-pl-realteam').val(player.realteam);
    $('#modal-pl-role').val(RoleNames[player.role]);
    
    plr_dlg.showModal();
}

function openDialog(id) {
    current_div = $('#'+id+'_div');
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
    current_div.html(`<div id="${current_div[0].id}_full" class="plr-full">\
                        <div class="plr-full-r1">\
                            <input type="text" id="${current_div[0].id}_name" class="inputFullName" value="${row.playername}">\
                            <input type="number" id="${current_div[0].id}_cost" class="inputFullAmount" value="${row.betamount}">\
                        </div>\
                        <div class="plr-full-r2">\
                            <input type="text" id="${current_div[0].id}_exp" class="inputFullExp" value="${row.exp_date}">\
                        </div>\
                        <div class="plr-full-r3">\
                            <input type="text" id="${current_div[0].id}_team" class="inputFullTeam" value="${row.team}">\
                        </div>\
                    </div>\
    `);
}

function calculate_expiration_date() {
    const now = new Date()
    return new Date(new Date(now).setDate(now.getDate() + 3)).toLocaleString() //TODO nighttime
}

function sendBet(amount) {
    const token = Cookies.get('csrftoken');
    const row = new Object()
    row.playername = $('#modal-pl-name').val();
    row.playerid = $('#modal-pl-id').val();
    row.betamount = amount;
    row.exp_date = calculate_expiration_date();
    row.team = $('#user_team_id').val();
    jsonData = JSON.stringify(row);

    var data = {'jsonData':jsonData, 'csrfmiddlewaretoken':token};

    $.post("/l4m/auction/sendBet/", data, function(response){
        });

    plr_dlg.close();
    dlg.close();

    set_div(row);
}