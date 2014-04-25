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
                
                // Case: SUCCESS
                $("#totalSum").text(data['total']);
                $("#last_id").text(data["id"]);
                var message = 'Added: ' + data['description'] + ' ' + data['amount'] + ' ' + data['category'];
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
                $("#addSuccess").fadeOut(300, function() {
                    $("#totalSum").text(data['total']);
                });
            }
        });      
    }
});

