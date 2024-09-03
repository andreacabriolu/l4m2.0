let dlg;
let search;
let player;

window.addEventListener('DOMContentLoaded', event => {

    dlg = document.getElementById('dlg open');
    plr_dlg = document.getElementById('dlg_player open');
    search = document.getElementById('modal-ob-search');

    gkdivs = document.getElementsByClassName('gk-div');
    gkcont = document.getElementById('gks');

    gkcont.addEventListener("click", function (e) {
        openDialog(e['id']);
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

function openDialog(e) {
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

function sendBet(amount) {
    const token = Cookies.get('csrftoken');
    const row = new Object()
    row.playerid = $('#modal-pl-id').val();
    row.betamount = amount;
    jsonData = JSON.stringify(row);

    var data = {'jsonData':jsonData, 'csrfmiddlewaretoken':token};

    $.post("/l4m/auction/sendBet/", data, function(response){
        });

    plr_dlg.close();
}