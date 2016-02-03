$(document).ready(function() {
    $('#teddy').hover(
        function() {
            $('#teddy').attr('src', "{{ url_for('static', filename='img/teddy_bear_happy.svg') }}");
        },
        function() {
            $('#teddy').attr('src', "{{ url_for('static', filename='img/teddy_bear.svg') }}");
        }
    );

    $('#arrow').on('click', function() {
        $.scrollTo($('.brownAPIsFooter').offset().top, 400);
    });

    $('#jobs').on('click', function() {
        $('#body').load("/static/html/jobs.html");
        $.scrollTo(0, 400);
    });
});