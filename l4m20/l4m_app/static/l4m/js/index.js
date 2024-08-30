window.addEventListener('DOMContentLoaded', event => {

    gkdivs = document.getElementsByClassName('gk-div');
    gkcont = document.getElementById('gks');

    gkcont.addEventListener("click", function (e) {
        openDialog(e['id']);
    })
})

var modal = document.getElementById('modal-ob-search');


function openDialog(e) {
    dlg = document.getElementById('dlg open');
    dlg.showModal();
}

var closeM = document.getElementsByClassName("close")[0];
closeM.onclick = function() {
    modal.style.display = "none";
  }

function searchPlayer() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('modal-ob-search');
    filter = input.value.toUpperCase();
    dl = document.getElementById("dataList");
    dt = dl.getElementsByTagName('dt');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < dt.length; i++) {
        a = dt[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            dt[i].style.display = "";
        } else {
            dt[i].style.display = "none";
        }
    }
}

