
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

window.addEventListener('DOMContentLoaded', event => {

    $('#mods').on('change', function () {
        var val = $(this).val();

        manage_mod(val);

    });

    $('#l_ups select').on('change', function () {
        removeSelectedOptionsFromOtherDropdowns($(this));
    });



})