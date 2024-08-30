window.addEventListener('DOMContentLoaded', event => {

    gkdivs=document.getElementsByClassName('gk-div');
    gkcont = document.getElementById('gks');

    gkcont.addEventListener("click", function(e) {
            openDialog(e['id']);
        })
    })


function openDialog(e){
    dlg=document.getElementById('dlg open');
    dlg.showModal();
  }

