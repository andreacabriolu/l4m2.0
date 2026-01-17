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

function showInfoAlert(response) {
    $("#info-alert").prop('hidden', false);
    $('#span-info-alert').text(response);
    $("#info-alert").fadeTo(5000, 0.33, function () {
        $("#info-alert").prop('hidden', true);
    });
}

function buildForm(url, token, jsonData) {
    return $(`<form action='${url}' method='post'><input type='text' name='jsonData' value='${jsonData}' /><input type='hidden' name='csrfmiddlewaretoken' value='${token}' /></form>`);
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
            $(this).children('option').each(function () {
                if ($(this).data().id == currentid) {
                    $(this).hide();
                }
            });
        }
    });
}

function deleteItemFromDropdowns(current, allSelects) {
    var currentid = current.children('option:selected').data().id;

    allSelects.each(function (i) {

        if (!($(this).is(current))) {
            $(this).children('option').each(function () {
                if ($(this).data().id == currentid) {
                    $(this).hide();
                }
            });
        }

    });
}

function adjustOtherDropdowns(current, allSelects, hideOption = false) {
    var currentid = current.children('option:selected').data().id;

    // $('#l_ups select').each(function (i) {
    allSelects.each(function (i) {

        /* 1. Removing player selected in other options */
        if (!($(this).is(current))) {
            if ($(this).children('option:selected').data().id == currentid) {
                $(this).children(`[data-id="${currentid}"]`).each(function () {
                    $(this).parent().val('');
                    $(this).prop('selected', false);
                });
            }

            /* 2. Hide options */
            if (hideOption) {
                $(this).children('option').each(function () {
                    if ($(this).data().id == currentid) {
                        $(this).hide();
                    }
                });
            }
        }

    });
}

function adjust_captain(reset = true) {
    tits = []; //titolars...
    $('#main_lineup select:visible').each(function () {
        var id = $(this).children('option:selected').data().id;
        if (typeof id !== 'undefined') {
            tits.push(id);
        }
    });

    if (reset) {
        reset_captain();
    }

    $('#captain').children('option').each(function () {
        if (tits.includes($(this).data().id)) {
            $(this).show();
        }
    });

}

function load_overtime_lineup(lineup_ot) {
    lineup_ot.forEach((el, idx) => {
        $(`#overtime_${idx + 1}_pl`).children(`option[data-id=${el}]`);

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

        if (item == 'ot') {
            lineup[item].forEach((el) => {
                selected_overtime_players.add(el);
            });
            continue;
        }

        if (item == 'penalties') {
            lineup[item].forEach(el => {
                penalties_order.push(el);
            });
            continue;
        }

        pl = $(`#${item}`).children(`option[data-id=${lineup[item]}]`);
        if (pl.length <= 0) { continue; }
        $(`#${item}`).val(pl[0].value);
        if (pl.data().limit == "True") {
            $(`#${item}`).addClass('played');
            $(`#${item}`).prop('disabled', true);
            removeAlreadyPlayedPlayerFromOtherDropdowns(pl);
        }
    }
}

function load_last_lineup(comp_id = 1) {
    var last_lineup = "";
    var data = { 'comp': comp_id };

    $.get("/l4m/lineup/getLast/", data, function (response) {
        if (response.startsWith('error')) {
            showErrorAlert(response);
        }
        else {
            try {
                if (response == "") {
                    return;
                }

                last_lineup = JSON.parse(response);
                //check for late lineup here

                mod = last_lineup[0].mod;
                $('#mods').val(mod);
                manage_mod(mod);
                load_lineup(last_lineup[0]);
                load_options(last_lineup);
                adjust_captain(reset = false);
            }
            catch {
                showErrorAlert("ERRORE NEL CARICAMENTO DELLA FORMAZIONE");
            }

        }
    });
}

function reset_captain() {
    $('#captain').children('option').each(function () {
        if ($(this).val() != '') {
            $(this).hide();
        }
    });
    $('#captain').val('option');
}

function freeze_who_played() {
    $('#l_ups select').each(function () {
        if ($(this).children('option:selected').data().limit == 'True') {
            $(this).addClass('played');
        }
    });
}

function updateOrder() {
    document.querySelectorAll(".player").forEach((el, i) => {
        el.querySelector(".order").textContent = i + 1;
    });
}

function savePenaltiesOrder() {
    penalties_order = [...document.querySelectorAll(".name")].map(n => n.dataset.id);
    $('#penaltiesModal').modal('hide');
}


var selected_overtime_players = new Set(); //TODO: so BAD global variable!!
var penalties_order = []; //TODO: so BAD global variable again!!

window.addEventListener('DOMContentLoaded', event => {

    const token = Cookies.get('csrftoken');
    let overtimeWarning = false;

    var comp_id = $('#competition_id').val();
    var comp_to_sel = $('#select_comp').children(`option[data-id=${comp_id}]`);
    if (comp_to_sel.length <= 0) { return; }
    $('#select_comp').val(comp_to_sel[0].value);

    load_last_lineup(comp_id);
    reset_captain();

    // $('#secondary_lineup').children('div').each(function () {
    //     $(this).on('click', function () {savePenaltiesOrder
    //         $(this).children('select').toggleClass('bg-overtime-subtle');
    //     });
    // });

    const penList = document.getElementById("penaltyList");

    new Sortable(penList, {
        animation: 150,
        ghostClass: "sortable-ghost",
        onEnd: updateOrder
    });

    $('#select_comp').on('change', function () {
        var data = {
            'competition': $('#select_comp').children('option:selected').data().id,
        };

        jsonData = JSON.stringify(data);
        var url = '/l4m/lineup/';
        form = buildForm(url, token, jsonData);

        $('body').append(form);

        form.trigger('submit');

    });

    $('#mods').on('change', function () {
        var val = $(this).val();
        manage_mod(val);
        adjust_captain();
    });

    $('#l_ups select').on('change', (function () {
        adjustOtherDropdowns($(this), $('#l_ups select'));
        if ($('#captain').val() != null &&
            $(this).children('option:selected').data().id == $('#captain').children('option:selected').data().id) {
            adjust_captain();
        }
        else {
            adjust_captain(reset = false);
        }
    }));

    $('#secondary_lineup select').on('change', (function () {
        var changedPl = $(this).children('option:selected').data().id;
        if (selected_overtime_players.has(changedPl)) {
            selected_overtime_players.delete(changedPl);
            overtimeWarning = true;
        }
    }));

    $('#main_lineup select').on('change', (function () {
        if (overtime) {
            var changedPl = ($(this).children('option:selected').data().id) + "";

            if (selected_overtime_players.has(parseInt(changedPl))) {
                selected_overtime_players.delete(parseInt(changedPl));
                overtimeWarning = true;
            }

            //TODO: insert new player in penalties order if not already present, removing the old one
            if (penalties_order.length > 0) {
                if (!penalties_order.includes(changedPl)) {
                    //check old one
                    var currentTits = $('#main_lineup').children('div:visible').find('option:selected').map(function () {
                        return $(this).data().id + "";
                    }).get();
                    var oldPl = penalties_order.filter(value => !currentTits.includes(value));
                    if (oldPl.length == 1) {
                        //remove the old one
                        var index = penalties_order.indexOf(oldPl[0]);
                        if (index > -1) {
                            penalties_order.splice(index, 1);
                        }
                    }

                    //add new one at the end
                    penalties_order.push(changedPl);
                }
            }
        }
    }));

    $('#btnSaveLineup').on('click', function () {
        $(this).prop('disabled', true);
        var allFilled = true;
        var playerSlots = {};
        var options = {};
        var overtime = $('#overtime').val().toLowerCase() == 'true';

        if (overtime && selected_overtime_players.size == 0 && !overtimeWarning) {
            showPopupErrorAlert('ATTENZIONE: NON HAI SELEZIONATO I GIOCATORI PER I TEMPI SUPPLEMENTARI');
            $('#btnSaveLineup').prop('disabled', false);
            return false;
        }

        playerSlots = {
            mod: $("#mods").val()
        };

        $('#main_lineup').children('div:visible').each(function () {
            $(this).children('select').each(function () {
                if ($(this).val() == '') {
                    allFilled = false;
                }
            });

            if (!allFilled) {
                showPopupErrorAlert('RIEMPI TUTTI GLI SLOT TITOLARI PRIMA DI CONFERMARE');
                $('#btnSaveLineup').prop('disabled', false);
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

        if ($('#captain').val() != null) {
            playerSlots["captain"] = $('#captain').children('option:selected').data().id;
        }

        if (selected_overtime_players.size > 0) {
            playerSlots['ot'] = [];
        }

        selected_overtime_players.forEach(function (item, index) {
            playerSlots['ot'].push(item);
        });

        if (penalties_order.length > 0) {
            playerSlots['penalties'] = [];
        }

        penalties_order.forEach(function (item, index) {
            playerSlots['penalties'].push(item);
        });

        if (allFilled) {

            if (overtime) {
                window.confirmation = confirm("HAI RICONTROLLATO I GIOCATORI PER I TEMPI SUPPLEMENTARI E PER I TIRI DI RIGORE?");
                if (!window.confirmation) {
                    $('#btnSaveLineup').prop('disabled', false);
                    return false;
                }
            }

            options = {
                hideLineup: $('#hideLineupSwitch').is(':checked'),
                modNoGk: $('#modNoportSwitch').is(':checked'),
            };

            jsonPlayers = JSON.stringify(playerSlots);
            jsonOpts = JSON.stringify(options);

            allComp = $('#allCompSwitch').prop('checked');
            late_edit = $('#day_already_started').val();

            if (allComp) {
                all_comp_ids = [];
                $('#select_comp').children('option').each(function () { all_comp_ids.push($(this).data().id) });
                var data = { 'tits': jsonPlayers, 'all_comp_ids': JSON.stringify(all_comp_ids), 'options': jsonOpts, 'csrfmiddlewaretoken': token };

                $.post("/l4m/lineup/saveMultiple/", data, function (response) {
                    if (response.startsWith('error')) {
                        showErrorAlert(response);
                    }
                    else {
                        if (response === "overtime") {
                            showPopupErrorAlert("FORMAZIONE SCHIERATA CORRETTAMENTE PER TUTTE LE COMPETIZIONI! ATTENZIONE: VERIFICARE TEMPI SUPPLEMENTARI E RIGORI");
                        } else {
                            showPopupErrorAlert("FORMAZIONE SCHIERATA CORRETTAMENTE PER TUTTE LE COMPETIZIONI!");
                        }
                        $('#btnSaveLineup').prop('disabled', false);
                    }
                });

            }
            else {
                var data = {
                    'tits': jsonPlayers, 'comp_id': comp_id, 'late_edit': late_edit,
                    'options': jsonOpts, 'csrfmiddlewaretoken': token
                };

                $.post("/l4m/lineup/save/", data, function (response) {
                    if (response.startsWith('error')) {
                        showErrorAlert(response);
                    }
                    else {
                        showPopupErrorAlert("FORMAZIONE SCHIERATA CORRETTAMENTE!");
                        $('#btnSaveLineup').prop('disabled', false);
                    }
                });
            }
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

    $('#penaltiesModal').on('show.bs.modal', function (e) {

        $('#penaltyList').empty();

        // Load saved order if any
        if (penalties_order.length > 0 && penalties_order.length == 11) {
            penalties_order.forEach(function (item, index) {
                var pl = $(`#main_lineup`).children('div:visible').find(`option:selected[data-id=${item}]`);
                if (pl.length > 0 && pl.data().id != undefined) {
                    var playerDiv = `<div class="player"><span class="order">${index + 1}</span>
                    <span class="name" data-id="${pl.data().id}">${pl.text()}</span>
                    <i class="fas fa-grip-lines drag"></i></div>`;

                    $('#penaltyList').append(playerDiv);
                }
            });
            return;
        }

        // Otherwise, load from current lineup
        $('#main_lineup').children('div:visible').each(function (idx) {
            var pl = $(this).children().children('option:selected');
            if (pl.length > 0 && pl.data().id != undefined) {
                var playerDiv = `<div class="player"><span class="order">${idx + 1}</span>
                <span class="name" data-id="${pl.data().id}">${pl.text()}</span>
                <i class="fas fa-grip-lines drag"></i></div>`;
                $('#penaltyList').append(playerDiv);
            }
        });

    });

    $('#overtimeModal').on('show.bs.modal', function (e) {

        var overtime_players = [];

        const secondary_valid_players = $('#secondary_lineup > div').filter(function () {
            const idOk = !this.id.startsWith('gk');
            const select = $(this).children('select').first();
            const notPlayed = !select.hasClass('played');

            return idOk && notPlayed;
            });


        // Collect players from secondary lineup, excluding goalkeepers (and (tentatively) already played)
        secondary_valid_players.each(function () {
            var sec_pl = $(this).children().children('option:selected');
            if (sec_pl.length > 0 && sec_pl.data().id != undefined) {
                overtime_players.push(sec_pl);
            }
        });

        $('#overtimeModal').find('.player-select').each(function (index) {
            $(`#overtime_${index + 1}_pl`).prop('disabled', false);

            if ($(this).children('option:selected').val() == '') {
                $(this).children('option:not(:first)').remove();
                $.each(overtime_players, function (index, o_player) {
                    $(this).append(o_player.clone());
                }.bind(this));
            }
        });

        Array.from(selected_overtime_players).forEach(function (item, index) {
            pl = $(`#overtime_${index + 1}_pl`).children(`option[data-id=${item}]`);
            if (pl.length <= 0) { return; }
            $(`#overtime_${index + 1}_pl`).val(pl[0].value);
            $(`#overtime_${index + 1}_pl`).prop('disabled', true);
        });

        $('#overtimeModal').find('.player-select').each(function (index) {
            if ($(this).children('option:selected').val() != '') {
                adjustOtherDropdowns($(this), $('#overtimeModal').find('.player-select'), hideOption = true);
            }
        });

        $('#overtimeModal').find('.player-select').on('change', function () {
            adjustOtherDropdowns($(this), $('#overtimeModal').find('.player-select'), true);
            $(this).off('change');
            $(this).prop('disabled', true);
            selected_overtime_players.add($(this).children('option:selected').data().id);
        });

        $('#btnResetOvertime').on('click', function () {
            $('#overtimeModal').find('.player-select').each(function () {
                $(this).val('');
                $(this).prop('disabled', false);
                selected_overtime_players = new Set();
            });
        });

        $('#btnConfirmOvertime').on('click', function () {
            $('#overtimeModal').modal('hide');
        });

    });

})