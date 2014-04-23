$(document).ready(function() {

    setInitialTags();

    function setInitialTags() {
        tags = $("#initialTags").find("span").each(function() {
            $("#tagsInput").tagsinput('add', $(this).text());
        });
    }

    // On Submit
    $("#newForm").submit(function(ev) {
        ev.preventDefault();
        // Submit the form, get back the total amount
        // clear the form and set the new total amount
        // Set a little message
        data = $("#newForm").serialize();
        $("#newForm")[0].reset();
        $("#tagsInput").tagsinput('removeAll');
        setInitialTags();

        $.ajax({
            type: "POST",
            url: "new",
            data: data,
            success: function(data) {
              $("#totalSum").text(data['total']);
              $("#last_id").text(data["id"]);
              $("#last_description").text(data['description']);
              $("#last_amount").text(data['amount']);
              $("#last_category").text(data['category']);
              $("#lastEntryDiv").hide().fadeIn(300);
            }
        });
    });

    // On Undo
    $("#last_undo button").click(function(ev) {
        ev.preventDefault();

        data = "id="+$("#last_id").text();

        $.ajax({
            type: "POST",
            url: "remove",
            data: data,
            success: function(data) {
                $("#lastEntryDiv").fadeOut(300, function() {
                    $("#totalAmount").text("Total is " + data['total']);
                    $("#last_description").text("");
                    $("#last_amount").text("");
                    $("#last_category").text("");
                });
            }
        });
    });
});

