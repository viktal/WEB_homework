$(".anlike-click").click(function (event) {
    $.ajax({
        url: 'http://127.0.0.1:8000/answer_like/',
        data: {"anlike-id": event.target.getAttribute("anlike-id")},
        type: 'post',
        success: function (data) {
            var click_id = event.target.getAttribute("anlike-id");
            var new_value = parseInt($('#' + click_id).text()) + 1;
            if (new_value > 0) {
                $('#' + click_id).text("+" + String(new_value));
            } else {
                $('#' + click_id).text(String(new_value));
            }
            var obj = $(event.target).parent()
            obj.css('color', '#12b706');
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });
});

$(".andislike-click").click(function (event) {
    $.ajax({
        url: 'http://127.0.0.1:8000/answer_dislike/',
        data: {"andislike-id": event.target.getAttribute("andislike-id")},
        type: 'post',
        success: function (data) {
            var click_id = event.target.getAttribute("andislike-id");
            var new_value = parseInt($('#' + click_id).text()) - 1;
            if (new_value > 0) {
                $('#' + click_id).text("+" + String(new_value));
            } else {
                $('#' + click_id).text(String(new_value));
            }
            var obj = $(event.target).parent()
            obj.css('color', '#e51f09');
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });
});

$(".correct-click").click(function (event) {
    $.ajax({
        url: 'http://127.0.0.1:8000/answer_correct/',
        data: {"correct-id": event.target.getAttribute("correct-id")},
        type: 'post',
        success: function (data) {
            // var obj = event.target.parent().parent();
            var obj = $(event.target).parent().parent();
            var button = obj.children();
            button.attr('class', 'visible');
            // button.text("hgjfdks");
            var icon = button.next();
            icon.attr('class', 'invisible');
            // icon.text("fhjdsk");

            console.log("Correct!")
        },
        failure: function (data) {
            alert('Got an error dude');
        }
    });
});
