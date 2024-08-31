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

    var closes = document.getElementsByClassName("close");
    
    closes.forEach(close => {
        closeM.onclick = function() {
            dlg.close();
            search.value='';
    }}); 

  $('.dt-content').on('click', function() {
    player_id = $(this)[0].dataset.id;

    openPlayerDialog(player_id);
  });

})

function openPlayerDialog(id){
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
    
    // $('#modal-pl-id').val = e;
}

