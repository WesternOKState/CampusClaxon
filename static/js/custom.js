$(function () {
    $('.footable').footable();
    addRowToggle: false
});

$(function () {
    $('table').footable();
    $('table').trigger('footable_clear_filter');
    $('.toggle').click(function () {
        $('.toggle').toggle();
        $('table').trigger($(this).data('trigger')).trigger('footable_redraw');
    });
});
//
// {#        $('tr').click(function () {#}
// {#            window.location = $(this).find('a').attr('href');#}
// {#        }).hover(function () {#}
// {#            $(this).toggleClass('hover');#}
// {#        });#}

//$(".form-control:first").focus();


function initialize() {
    $(".id_template").change(function () {
        alert("Change to page /sendAlert/" + $(".id_template").val())
        //window.location("/sendAlert/"+$(".id_template").val())
    })
}