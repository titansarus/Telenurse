const paint_elements = (new_color) => {
    let $sidebar = $('.sidebar');
    let $main_panel = $('.main-panel');
    let $full_page = $('.full-page');
    let $sidebar_responsive = $('body > .navbar-collapse');
    
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

const init_theme = (username) => {
    $('.light-badge').click(function () {
        $('body').addClass('white-content');
        localStorage.setItem(`${username}-themePreference`, "light");
    });
    
    $('.dark-badge').click(function () {
        $('body').removeClass('white-content');
        localStorage.setItem(`${username}-themePreference`, "dark");
    });

    $('.fixed-plugin .background-color span').click(function () {
        $(this).siblings().removeClass('active');
        $(this).addClass('active');

        var new_color = $(this).data('color');
        localStorage.setItem(`${username}-colorPreference`, new_color);

        paint_elements(new_color);
    });

    let theme = localStorage.getItem(`${username}-themePreference`);
    if (theme === "light") {
        $('body').addClass('white-content');
    }

    let color = localStorage.getItem(`${username}-colorPreference`);
    if (color) {
        paint_elements(color);
    }
}