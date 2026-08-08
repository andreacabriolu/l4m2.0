window.addEventListener('DOMContentLoaded', event => {

    const token = Cookies.get('csrftoken');

    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        // Uncomment Below to persist sidebar toggle between refreshes
        // if (localStorage.getItem('sb|sidebar-toggle') === 'true') {
        //     document.body.classList.toggle('sb-sidenav-toggled');
        // }
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

    const onlineUsersToggle =
        document.getElementById("onlineUsersToggle");

    const onlineUsersList =
        document.getElementById("onlineUsersList");

    const onlineUsersChevron =
        document.getElementById("onlineUsersChevron");


    onlineUsersToggle?.addEventListener("click", () => {

        const expanded =
            onlineUsersToggle.getAttribute("aria-expanded") === "true";

        onlineUsersToggle.setAttribute(
            "aria-expanded",
            String(!expanded)
        );

        onlineUsersList.hidden = expanded;

        onlineUsersChevron.classList.toggle(
            "fa-chevron-down",
            expanded
        );

        onlineUsersChevron.classList.toggle(
            "fa-chevron-up",
            !expanded
        );

    });


});

class Utilities {
    static buildForm(url, token, jsonData) {

        return $('<form action="' + url + '" method="post">' +
            '<input type="text" name="jsonData" value="' + jsonData + '" />' +
            '<input type="hidden" name="csrfmiddlewaretoken" value="' + token + '" />' +
            '</form>');
    }
}

function updateOnlineUsers(data) {

    const count = document.getElementById("onlineUsersCount");
    const list = document.getElementById("onlineUsersList");

    if (!count || !list)
        return;

    count.textContent = data.count;

    list.innerHTML = data.teams
        .map(teamname => `
            <div class="online-user">
                <span class="online-user-dot"></span>
                <span>${teamname}</span>
            </div>
        `)
        .join("");
}

async function sendHeartbeat() {

    try {

        const response = await fetch("/l4m/heartbeat/", {
            method: "POST",
            headers: {
                "X-CSRFToken": Cookies.get("csrftoken"),
                "X-Requested-With": "XMLHttpRequest"
            }
        });

        if (!response.ok)
            return;

        const data = await response.json();

        updateOnlineUsers(data);

    }
    catch (error) {

        console.error("Heartbeat error:", error);

    }
}

sendHeartbeat();

setInterval(sendHeartbeat, 60000);