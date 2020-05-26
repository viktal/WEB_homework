$(".like-click").click(function (event) {
    $.ajax({
        url: 'http://127.0.0.1/like/',
        data: {"like-id": event.target.getAttribute("like-id")},
        type: 'post', // This is the default though, you don't actually need to always mention it
        success: function (data) {
            var click_id = event.target.getAttribute("like-id");
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

$(".dislike-click").click(function (event) {
    $.ajax({
        url: 'http://127.0.0.1/dislike/',
        data: {"dislike-id": event.target.getAttribute("dislike-id")},
        type: 'post', // This is the default though, you don't actually need to always mention it
        success: function (data) {
            var click_id = event.target.getAttribute("dislike-id");
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