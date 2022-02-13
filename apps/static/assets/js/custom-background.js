$sidebar = $('.sidebar');
$main_panel = $('.main-panel');
$full_page = $('.full-page');
$sidebar_responsive = $('body > .navbar-collapse');

const paint_elements = (new_color) => {
    if ($sidebar.length != 0) {
        $sidebar.attr('data', new_color);
    }

    if ($main_panel.length != 0) {
        $main_panel.attr('data', new_color);
    }

    if ($full_page.length != 0) {
        $full_page.attr('filter-color', new_color);
    }

    if ($sidebar_responsive.length != 0) {
        $sidebar_responsive.attr('data', new_color);
    }
}

const init_theme = () => {
    $('.light-badge').click(function () {
        $('body').addClass('white-content');
        localStorage.setItem("themePreference", "light");
    });
    
    $('.dark-badge').click(function () {
        $('body').removeClass('white-content');
        localStorage.setItem("themePreference", "dark");
    });

    $('.fixed-plugin .background-color span').click(function () {
        $(this).siblings().removeClass('active');
        $(this).addClass('active');

        var new_color = $(this).data('color');
        localStorage.setItem("colorPreference", new_color);

        paint_elements(new_color);
    });

    let theme = localStorage.getItem("themePreference");
    if (theme === "light") {
        $('body').addClass('white-content');
    }

    let color = localStorage.getItem("colorPreference");  // primary-blue-green
    console.log(color)
    if (color) {
        paint_elements(color);
        alert('done')
    }
}