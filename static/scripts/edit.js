$(document).ready(function() {

    setInitialTags();

    function setInitialTags() {
        tags = $("#initialTags").find("span").each(function() {
            $("#tagsInput").tagsinput('add', $(this).text());
        });
    }

    // On Submit
    $("#editForm").submit(function(ev) {
        ev.preventDefault();
        data = $("#editForm").serialize();

        $.ajax({
            type: "POST",
            url: $("#editForm").attr("action"),
            data: data,
            success: function(data) {
                $("#amount").val(data["amount"]);
                $("#category").val(data["category"]);
                $("#description").val(data["description"]);

                if (data["message"] == "success") {
                    $("#editSuccess").fadeIn(200);
                    setTimeout(function() { window.location.replace("/history"); }, 3000);
                }
            }
        });
    });

    // On Remove
    $("#removeButton").click(function(ev) {
        ev.preventDefault();

        var id = $("#editForm").attr("action").split("=")[1];

        $.ajax({
            type: "POST",
            url: "remove?id="+id,
            success: function(data) {
                if (data["message"] == "success") {
                    $("#removeSuccess").fadeIn(200);
                    setTimeout(function() { window.location.replace("/history"); }, 3000);
                }
            }
        });
    });
});

