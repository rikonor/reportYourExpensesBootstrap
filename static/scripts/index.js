$(document).ready(function() {
    $("#newForm").submit(function(ev) {
        ev.preventDefault();
    
        // Submit the form, get back the total amount
        // clear the form and set the new total amount
        // Set a little message
        data = $("#newForm").serialize();
        $("#newForm")[0].reset();

        $.ajax({
            type: "POST",
            url: "new",
            data: data,
            success: function(data) {
                $("#totalAmount").text("Total is " + data);
            }
        });
    });
});

