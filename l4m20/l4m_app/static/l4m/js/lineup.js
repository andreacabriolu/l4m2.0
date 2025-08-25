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

function showInfoAlert(response) {
    $("#info-alert").prop('hidden', false);
    $('#span-info-alert').text(response);
    $("#info-alert").fadeTo(5000, 0.33, function () {
        $("#info-alert").prop('hidden', true);
    });
}

function manage_mod(val) { //show and hide, TODO: real the best way?

    nums = val.split('-');
    ndif = parseInt(nums[0]);
    ncen = parseInt(nums[1]);
    natt = parseInt(nums[2]);
    let max_dif_ris = 5;
    let max_cen_ris = 5;
    let max_att_ris = 5;

    //DIF
    for (i = 4; i <= ndif; i++) {
        $(`#d${i}`).prop('hidden', false);
        // $(`#d${max_dif_ris--}r`).prop('hidden',true);
    }
    for (i = ndif + 1; i <= 5; i++) {
        $(`#d${i}`).prop('hidden', true);
        // $(`#d${i}r`).prop('hidden',false);
    }

    //CC
    for (i = 4; i <= ncen; i++) {
        $(`#c${i}`).prop('hidden', false);
        // $(`#c${max_cen_ris--}r`).prop('hidden',true);
    }
    for (i = ncen + 1; i <= 5; i++) {
        $(`#c${i}`).prop('hidden', true);
        // $(`#c${i}r`).prop('hidden',false);
    }

    //ATT
    for (i = 2; i <= natt; i++) {
        $(`#a${i}`).prop('hidden', false);
        // $(`#a${max_att_ris--}r`).prop('hidden',true);
    }
    for (i = natt + 1; i <= 5; i++) {
        $(`#a${i}`).prop('hidden', true);
        // $(`#a${i}r`).prop('hidden',false);
    }

}

let options_ids = {
    'gk': [],
    'def': [],
    'cc': [],
    'fw': []
}

function fill_options() {
    $('#gk_tit').children('option').each(function () {
        options_ids['gk'].push($(this).data().id);
    });

    $('#d1_tit').children('option').each(function () {
        options_ids['def'].push($(this).data().id);
    });

    $('#c1_tit').children('option').each(function () {
        options_ids['cc'].push($(this).data().id);
    });

    $('#a1_tit').children('option').each(function () {
        options_ids['fw'].push($(this).data().id);
    });
}

function removeSelectedOptionsFromOtherDropdowns(current) {

    var id = current.children('option:selected').data().id;
    $('#l_ups select').each(function (i) {
        if (!($(this).is(current))) {
            if ($(this).children('option:selected').data().id == id) {
                $(this).children(`[data-id="${id}"]`).each(function () {
                    $(this).parent().val('');
                    $(this).prop('selected', false);
                });
            }
        }
    });
}

function removeAlreadyPlayedPlayerFromOtherDropdowns(item) {
    var currentid = item.data().id;
    $('#l_ups select').each(function () {

        if (!($(this).is(item.prevObject))) {
                $(this).children('option').each(function() {
                    if ($(this).data().id == currentid) {
                        $(this).hide(); 
                    }
                });
                // $(this).children(`[data-id="${currentid}"]`).each(function () {
                //     $(this).parent().val('');
                //     $(this).prop('selected', false);
                // });
            }
    });
}

function adjustOtherDropdowns(current) {
    var currentid = current.children('option:selected').data().id;

    $('#l_ups select').each(function (i) {

        /* 1. Removing player selected in other options */
        if (!($(this).is(current))) {
            if ($(this).children('option:selected').data().id == currentid) {
                $(this).children(`[data-id="${currentid}"]`).each(function () {
                    $(this).parent().val('');
                    $(this).prop('selected', false);
                });
            }
        }

    });


}

function adjust_captain(reset=true) {
    tits = []; //titolars...
    $('#main_lineup select:visible').each(function () {
        var id = $(this).children('option:selected').data().id;
        if (typeof id !== 'undefined') {
            tits.push(id);
        }
    });

    if(reset) {
        reset_captain();
    }

    $('#captain').children('option').each(function () {
        if (tits.includes($(this).data().id)) {
            $(this).show();
        }
    });

}

function load_options(lineup) {
    var hideLineup = lineup[2];
    var modNoGk = lineup[3];

    $('#hideLineupSwitch').attr('checked', hideLineup);
    $('#modNoportSwitch').attr('checked', modNoGk);
}

function load_lineup(lineup) {
    for (item in lineup) {
        if (item == "mod") { continue; }

        pl = $(`#${item}`).children(`option[data-id=${lineup[item]}]`);
        if (pl.length <= 0) { continue; }
        $(`#${item}`).val(pl[0].value);
        if(pl.data().limit == "True") {
            $(`#${item}`).addClass('played');
            $(`#${item}`).prop('disabled', true);
            removeAlreadyPlayedPlayerFromOtherDropdowns(pl);
        }
    }
}

function load_last_lineup() {
    var last_lineup = "";

    $.get("/l4m/lineup/getLast/", function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            try {
                if (response == "") {
                    return;
                }

                last_lineup = JSON.parse(response);

                mod = last_lineup[0].mod;
                $('#mods').val(mod);
                manage_mod(mod);
                load_lineup(last_lineup[0]);
                load_options(last_lineup);
                adjust_captain(reset=false);
            }
            catch {
                showErrorAlert("ERRORE NEL CARICAMENTO DELLA FORMAZIONE");
            }

        }
    });
}

function reset_captain() {
    $('#captain').children('option').each(function () {
        if($(this).val() != '') {
            $(this).hide(); 
        }
    });
    $('#captain').val('option');
}

function freeze_who_played() {
    $('#l_ups select').each(function () {
        if($(this).children('option:selected').data().limit == 'True') {
            $(this).addClass('played'); 
        }
    });
}

window.addEventListener('DOMContentLoaded', event => {

    const token = Cookies.get('csrftoken');

    load_last_lineup();
    reset_captain();

    $('#mods').on('change', function () {
        var val = $(this).val();
        manage_mod(val);
        adjust_captain();
    });

    $('#l_ups select').on('change', (function () {
        adjustOtherDropdowns($(this));
        if($('#captain').val() != null && 
           $(this).children('option:selected').data().id == $('#captain').children('option:selected').data().id) {
                adjust_captain();
        }
        else {
            adjust_captain(reset=false);
        }
    }));

    $('#btnSaveLineup').on('click', function () {
        var allFilled = true;
        var playerSlots = {};
        var options = {};

        playerSlots = {
            mod: $("#mods").val()
        };

        $('#main_lineup').children('div:visible').each(function () {
            $(this).children('select').each(function() {  
                if ($(this).val() == '') {
                    allFilled = false;
                }
            });

            if (!allFilled) {
                showPopupErrorAlert('RIEMPI TUTTI GLI SLOT TITOLARI PRIMA DI CONFERMARE');
                return false;
            }

            if ($(this).get(0).hidden == false) {
                slot = $(this).children().get(0).id;
                id = $(this).children().children('option:selected').data().id;
                playerSlots[slot] = id;
            }
        });

        $('#secondary_lineup').children().each(function () {
            slot = $(this).children().get(0).id;
            id = $(this).children().children('option:selected').data().id;
            playerSlots[slot] = id;
        });

        if($('#captain').val() == null) {
            // showPopupErrorAlert('IMPOSTA IL CAPITANO'); TODO: check with giamba
            // return false;
        }

        if($('#captain').val() != null) {
            playerSlots["captain"] = $('#captain').children('option:selected').data().id;
        }

        if (allFilled) {
            options = {
                hideLineup: $('#hideLineupSwitch').is(':checked'),
                modNoGk: $('#modNoportSwitch').is(':checked'),
            };

            jsonPlayers = JSON.stringify(playerSlots);
            jsonOpts = JSON.stringify(options);

            var data = { 'tits': jsonPlayers, 'options': jsonOpts, 'csrfmiddlewaretoken': token };

            $.post("/l4m/lineup/save/", data, function (response) {
                if (response.startsWith('error')) {
                    showErrorAlert(response);
                }
                else {
                    showInfoAlert("FORMAZIONE SCHIERATA CORRETTAMENTE!");
                }
            });
        }

    });

    $('#btnResetLineup').on('click', function () {
        $('#main_lineup').each(function () {
            $(this).children().children().val('');
        });

        $('#secondary_lineup').each(function () {
            $(this).children().children().val('');
        });

        reset_captain();
    });

    $('#btnResetMainLineup').on('click', function () {
        $('#main_lineup').each(function () {
            $(this).children().children().val('');
        });

        reset_captain();
    });

})