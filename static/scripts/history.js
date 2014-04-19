$(document).ready(function() {

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

        eRows.fadeOut(200, function() {
            eRows.empty();
            for (var i = 0; i < data.length; i++) {
                eRows.append(buildRow(data[i]));
            }
            eRows.fadeIn(200);
        });
    }

    function buildRow(obj) {
        tags = obj["tags"];
        tagLinks = "";
        for (var i = 0; i < tags.length; i++) {
            tagLinks += '<a href="byTag?tag=">'+tags[i]+'</a>';
        }
        row = '<tr><td>'+obj["created"]+'</td><td>'+obj["description"]+'</td><td>'+obj["amount"]+'</td><td>'+obj["category"]+'</td><td>'+tagLinks+'</td></tr>';
        return row;
    }
});

