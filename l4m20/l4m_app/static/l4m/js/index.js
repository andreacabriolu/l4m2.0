let dlg;
let search;

window.addEventListener('DOMContentLoaded', event => {

    dlg = document.getElementById('dlg open');
    search = document.getElementById('modal-ob-search');

    gkdivs = document.getElementsByClassName('gk-div');
    gkcont = document.getElementById('gks');

    gkcont.addEventListener("click", function (e) {
        openDialog(e['id']);
    })

    var closeM = document.getElementsByClassName("close")[0];
    
    closeM.onclick = function() {
        dlg.close();
        search.value='';
  }
})

function openDialog(e) {
    dlg.showModal();
}

function searchPlayer() {
    var filter, i, txtValue;
    filter = search.value.toUpperCase();
    dl = document.getElementById("dataList");
    dt = dl.getElementsByTagName('dt');

    // Loop through all list items, and hide those who don't match the search query
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

