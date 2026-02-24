
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
    // let rankingDataTable;
    const token = Cookies.get('csrftoken');

    var comp_id = $('#comp').val();

    // $('#select_series').on('change', function () {
    //     rankingDataTable.ajax.reload();
    //     calendarDataTable.ajax.reload();
    // });

    const gironiPanel = document.getElementById("gironi-panel");
    const finalPanel = document.getElementById("fase-finale-panel");
    const stageButtons = document.querySelectorAll(".stage-pill");

    let rankingTable = null;
    let calendarTable = null;
    let bracketInitialized = false;

    stageButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            gironiPanel
                .classList.toggle("d-none", btn.dataset.stage !== "girone");

            finalPanel
                .classList.toggle("d-none", btn.dataset.stage !== "fase-finale");
        });
    });

    document.querySelectorAll(".group-pill").forEach(btn => {

    btn.addEventListener("click", () => {

        const groupId = btn.dataset.group;

        document.querySelectorAll(".group-pill")
            .forEach(p => p.classList.remove("active"));

        btn.classList.add("active");

        document.querySelectorAll(".group-content")
            .forEach(content => content.classList.add("d-none"));

        document.getElementById(groupId)
            .classList.remove("d-none");

        document.getElementById(groupId)
            .scrollIntoView({ behavior: "smooth", block: "start" });

        });

    });




    // stageButtons.forEach(btn => {
    //     btn.addEventListener("click", () => {
    //         const stage = btn.dataset.stage;

    //         stageButtons.forEach(b => b.classList.remove("active"));
    //         btn.classList.add("active");

    //         if (stage === "girone") {
    //             showGironi();
    //         } else {
    //             showFinal();
    //         }
    //     });
    // });

    // function showGironi() {
    //     finalPanel.classList.add("d-none");
    //     gironiPanel.classList.remove("d-none");

    //     if (!rankingTable) {
    //         initializeGironiTables();
    //     } else {
    //         rankingTable.columns.adjust();
    //         calendarTable.columns.adjust();
    //     }
    // }

    // function showFinal() {
    //     gironiPanel.classList.add("d-none");
    //     finalPanel.classList.remove("d-none");

    //     if (!bracketInitialized) {
    //         initializeBracket();
    //         bracketInitialized = true;
    //     }
    // }

    function initializeGironiTables() {
        // rankingTable = $("#rankingTable").DataTable({
        //     responsive: true,
        //     autoWidth: false
        // });

        calendarTable = $("#calendarTable").DataTable({
            responsive: true,
            autoWidth: false
        });
    }

    function initializeBracket() {
        const container = document.getElementById("bracketContainer");

        container.innerHTML = `
        <div class="bracket">
  <div class="bracket-round">
    <div class="bracket-round-title">Quarterfinals</div>

    <div class="bracket-match">
      <div class="bracket-team winner">
        Team A <span class="bracket-score">2</span>
      </div>
      <div class="bracket-team">
        Team B <span class="bracket-score">1</span>
      </div>
    </div>
  </div>

  <div class="bracket-round final">
    <div class="bracket-round-title">Final</div>

    <div class="bracket-match final">
      <div class="bracket-trophy">🏆</div>
      <div class="bracket-champion">TEAM A</div>
    </div>
  </div>
</div>

    `;
    }



    $(function () {
        // rankingDataTable = $('#rankingDataTable').DataTable(
        //     {
        //         paging: false,
        //         searching: false,
        //         layout: {
        //             bottomStart: null,
        //         },
        //         order: [
        //             [1, 'desc'], //Punti
        //             [2, 'desc'] //Fantapunti
        //         ],
        //         ajax: {
        //             url: "/l4m/retrieveRankingInfo/",
        //             type: 'POST',
        //             data: function (d) {
        //                 d.c_id = comp_id,
        //                     d.s_id = $('#select_series').children('option:selected').data().id,
        //                     d.day = $('#day').val(),
        //                     d.csrfmiddlewaretoken = token
        //             },
        //             dataSrc: "lines",
        //         },
        //         columnDefs: [
        //             { className: "dt-teamname", targets: [0] },
        //             { className: "dt-teampt", targets: [1] },
        //         ],
        //         initComplete: function (settings, json) {
        //             $('#team_h_camp').removeClass('dt-teamname');
        //             $('#team_fp_h_camp').removeClass('dt-teampt');
        //         },
        //     }
        // );

        var groupColumn = 0;
        calendarDataTable = $('#calendarDataTable').DataTable(
            {
                paging: false,
                searching: false,
                ordering: false,
                layout: {
                    topStart: null,
                    bottomStart: null,
                },
                order: [
                    [groupColumn, 'asc'],
                ],
                drawCallback: function (settings) {
                    var api = this.api();
                    var rows = api.rows({ page: 'current' }).nodes();
                    var last = null;

                    api.column(groupColumn, { page: 'current' })
                        .data()
                        .each(function (group, i) {
                            if (last !== group) {
                                $(rows)
                                    .eq(i)
                                    .before(
                                        '<tr class="group"><td colspan="4">' +
                                        group +
                                        '</td></tr>'
                                    );

                                last = group;
                            }
                        });
                },
                ajax: {
                    url: "/l4m/retrieveCalendarInfo/",
                    type: 'GET',
                    data:
                        function (d) {
                            d.s_id = $('#select_series').children('option:selected').data().id,
                                d.day = $('#day').val(),
                                d.csrfmiddlewaretoken = token
                        },
                    dataSrc: "calendarlines",
                },
                columnDefs: [
                    { visible: false, targets: groupColumn },
                    { className: "dt-teamname-home-calendar", targets: [1] },
                    { className: "dt-teamname-away-calendar", targets: [4] },
                    { className: "dt-teampt-calendar", targets: [2, 3] },
                ],
                initComplete: function (settings, json) {
                    // $('#team_h_camp').removeClass('dt-teamname');
                    // $('#team_fp_h_camp').removeClass('dt-teampt');
                },
            }
        );

        $('#calendarDataTable tbody').on('click', 'tr.group', function () {
            var currentOrder = table.order()[0];
            if (currentOrder[0] === groupColumn && currentOrder[1] === 'asc') {
                table.order([[groupColumn, 'desc']]).draw();
            }
            else {
                table.order([[groupColumn, 'asc']]).draw();
            }
        });

    });
});