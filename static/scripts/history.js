$(document).ready(function() {

    bindTagButtons();

    function bindTagButtons() {
        $(".tagButton").click(function(ev) {
            var tag = $(this).text();
            $("#tagsInput").tagsinput("add", tag);
        });
    }

    $("#tagsInput").change(function() {
        data = $("#tagsInput").serialize();
        $.ajax({
            type: "GET",
            url: "JsonExpensesByTags",
            data: data,
            success: function(data) {
                rebuildTable(data);
            }
        });
    });

    function rebuildTable(data) {
        eRows = $("#expensesTable tbody");

        $("#totalSum").fadeOut(200);
        eRows.fadeOut(200, function() {
            eRows.empty();
            var sum = 0;
            for (var i = 0; i < data.length; i++) {
                eRows.append(buildRow(data[i]));
                sum += parseInt(data[i]["amount"]);
            }
            eRows.fadeIn(200);
            $("#totalSum").text(sum).fadeIn(200);

            bindTagButtons();
        });
    }

    function buildRow(obj) {
        tags = obj["tags"];
        tagLinks = "";
        for (var i = 0; i < tags.length; i++) {
            tagLinks += '<a class="tagButton">'+tags[i]+'</a>';
        }
        row = '<tr><td>'+obj["created"]+'</td><td>'+obj["description"]+'</td><td>'+obj["amount"]+'</td><td>'+obj["category"]+'</td><td>'+tagLinks+'</td><td><a href="/edit?id='+obj["id"]+'">Edit</a></td></tr>';
        return row;
    }
});

