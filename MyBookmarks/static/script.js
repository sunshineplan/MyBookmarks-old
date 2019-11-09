function my_categories() {
  categories = $.getJSON('/category/get', function (json) {
    $('#category').empty();
    $('#categories').empty();
    $.each(json, function (i, item) {
      $('#category').append($('<option>').prop('value', item.category));
      var $li = $("<li><a class='nav-link category' id='" + item.id + "'>" + item.category + ' (' + item.num + ')' + '</a></li>')
      $li.appendTo('#categories');
    });
  });
};
function my_bookmarks(category_id = -1) {
  if (category_id == -1) {
    url = '/bookmark/get';
    $('#edit_category').prop('hidden', true);
    $('#add_bookmark').prop('href', function () {
      return '/bookmark/add';
    });
  } else {
    url = '/bookmark/get/' + category_id;
    $('#edit_category').prop('hidden', false);
    $('#edit_category').prop('href', '/category/edit/' + category_id);
    $('#add_bookmark').prop('href', function () {
      return '/bookmark/add' + '?category_id=' + category_id;
    });
  };
  bookmarks = $.getJSON(url, function (json) {
    document.title = json.category + ' - My Bookmarks';
    $('#title').text(json.category);
    $('#bookmarks').empty();
    $.each(json.bookmarks, function (i, item) {
      var $tr = $("<tr onclick='window.open(&quot;" + item.url + "&quot);'>").append(
        $('<td>').text(item.bookmark),
        $('<td>').text(item.url),
        $('<td>').text(item.category)
      );
      $tr.appendTo('#bookmarks');
    });
  });
};
