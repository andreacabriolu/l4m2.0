
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


window.addEventListener('DOMContentLoaded', event => {
    const token = Cookies.get('csrftoken');
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    $(function () {
        var rankingDataTable = $('#rankingDataTable').DataTable(
            {
                paging: false,
                searching: false,
                layout: {
                    bottomStart: null,
                },
                // columnDefs: [
                //     // {
                //     //     orderable: false,
                //     //     render: DataTable.render.select(),
                //     //     targets: 0
                //     // },
                //     // {
                //     //     target: 2,
                //     //     visible: false
                //     // }
                // ],
                // pageLength: 10,
                // select: {
                //     // style: 'multi',
                //     // selector: 'td:first-child',
                //     // headerCheckbox: 'select-page'
                // },
                order: [[7, 'desc']],
                // // createdRow: function (row, data, dataIndex) {
                // //     if (data[1] == 'Activated') {
                // //         activatedHoursTot += data[4];
                // //         $(row).addClass('activated-row');
                // //     }
                // // },
                // ajax: {
                //     url: "/l4m/retrieveRankingInfo/",
                //     type: 'POST',
                //     data: { "c_id": $('#c_id').val(), 'csrfmiddlewaretoken': token },
                //     dataSrc: "data",
                // }
            }
        );
    });
})