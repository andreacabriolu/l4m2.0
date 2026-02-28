
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
                .classList.toggle("d-none", btn.dataset.stage !== "fase_finale");
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



});