function my_categories() {
  searchParams = new URLSearchParams(window.location.search);
  category = searchParams.get('category');
  categories = $.getJSON('/category/get', function (json) {
    $('#category-list').empty();
    $('#categories').empty();
    $('#-1.category').text('All Bookmarks (' + json.total + ')');
    $.each(json.categories, function (i, item) {
      $('#category-list').append($('<option>').prop('value', item.category));
      if (category == item.id) {
        var $li = $("<li><a class='nav-link category active' id='" + item.id + "'>" + item.category + ' (' + item.num + ')' + '</a></li>');
      } else {
        var $li = $("<li><a class='nav-link category' id='" + item.id + "'>" + item.category + ' (' + item.num + ')' + '</a></li>');
      };
      $li.appendTo('#categories');
    });
    if (category == null) {
      $('#-1.category').addClass('active')
    };
    if (category == 0) {
      $('#categories').append("<li><a class='nav-link category active' id=0>Uncategorized (" + json.uncategorized + ')' + '</a></li>');
    } else {
      $('#categories').append("<li><a class='nav-link category' id=0>Uncategorized (" + json.uncategorized + ')' + '</a></li>');
    };
  });
};
function my_bookmarks(category_id = -1) {
  if (category_id == -1) {
    location.href = '/';
  } else {
    location.href = '/?category=' + category_id;
  };
};
function simplify_url() {
  if (isMobile.matches) {
    $('.url').each(function() {
      $(this).text($(this).text().replace(/https?:\/\/(www\.)?/i, ''));
    });
  } else {
    $('.url').each(function() {
      $(this).text($(this).attr('href'));
    });
  };
};
