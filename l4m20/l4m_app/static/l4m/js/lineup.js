
function manage_mod(val) { //show and hide, TODO: real the best way?
    if(val == '3-4-3') {
        $('#d4').prop('hidden', true);
        $('#d5').prop('hidden', true);
        $('#d6').prop('hidden', true);
        $('#d7').prop('hidden', true);
        $('#d8').prop('hidden', true);

        $('#d4r').prop('hidden', false);
        $('#d5r').prop('hidden', false);
        $('#d6r').prop('hidden', false);
        $('#d7r').prop('hidden', false);
        $('#d8r').prop('hidden', false);

        $('#c4').prop('hidden', false);
        $('#c5').prop('hidden', true);
        $('#c6').prop('hidden', true);
        $('#c7').prop('hidden', true);
        $('#c8').prop('hidden', true);

        $('#c4r').prop('hidden', true);
        $('#c5r').prop('hidden', false);
        $('#c6r').prop('hidden', false);
        $('#c7r').prop('hidden', false);
        $('#c8r').prop('hidden', false);

        $('#a2').prop('hidden', false);
        $('#a3').prop('hidden', false);
        $('#a4').prop('hidden', true);
        $('#a5').prop('hidden', true);
        $('#a6').prop('hidden', true);

        $('#a4r').prop('hidden', true);
        $('#a5r').prop('hidden', true);
        $('#a6r').prop('hidden', true);


    }
}

window.addEventListener('DOMContentLoaded', event => {

    $('#mods').on('change', function(){
        var val = $(this).val();

        manage_mod(val);

    });

})