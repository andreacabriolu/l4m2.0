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

});

class Utilities {
    static buildForm(url, token, jsonData) {

        return $('<form action="' + url + '" method="post">' +
        '<input type="text" name="jsonData" value="'+jsonData+'" />' +
        '<input type="hidden" name="csrfmiddlewaretoken" value="'+token+'" />' +
        '</form>');
    }
}