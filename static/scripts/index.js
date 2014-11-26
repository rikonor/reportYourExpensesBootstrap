$(document).ready(function() {

    // On Submit
    $("#newForm").submit(function(ev) {
        ev.preventDefault();

        // serialize
        data = $("#newForm").serialize();

        // validate
        // Elaborate ---
        if (!$("#description")[0].value) return;

        $("#newForm")[0].reset();

        $.ajax({
            type: "POST",
            url: "new",
            data: data,
            success: function(data) {
                
                // Case: SUCCESS
                $("#last_id").text(data["id"]);
                var message = 'Added: ' + data['description'] + ' ' + data['category'];
                var button  = '<a class="pull-right" id="undoButton">Undo</a>';
                $("#addSuccess").html(message+button).fadeIn(300);
                $("#undoButton").click(undoLastAdd);
            }
        });
    });

    // On Undo
    function undoLastAdd() {
        data = "id="+$("#last_id").text();

        $.ajax({
            type: "POST",
            url: "remove",
            data: data,
            success: function(data) {
                $("#addSuccess").fadeOut(300);
            }
        });      
    }

    function getCategory() {
        selectBox = $("#category")[0];
        return selectBox.options[selectBox.selectedIndex].value;
    }

    // Geolocation
    function success(position) {
        var s = document.querySelector('#status');

        if (s.className == 'success') {
            // not sure why we're hitting this twice in FF, I think it's to do with a cached result coming back    
            return;
        }

        s.innerHTML = "found you!";
        s.className = 'success';

        var lat = position.coords.latitude;
        var lng = position.coords.longitude;

        $("#location")[0].value = lat + "," + lng;       
    }

    function error(msg) {
        var s = document.querySelector('#status');
        s.innerHTML = typeof msg == 'string' ? msg : "failed";
        s.className = 'fail';
    }

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        error('not supported');
    }
});