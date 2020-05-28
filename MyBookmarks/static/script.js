function my_categories() {
  $.getJSON('/category/get', function (json) {
    $('#category-list').empty();
    $('#categories').empty();
    $('#-1.category').text('All Bookmarks (' + json.total + ')');
    $.each(json.categories, function (i, item) {
      $('#category-list').append($('<option>').prop('value', item.category));
      var $li = $("<li><a class='nav-link category' id='" + item.id + "'>" + item.category + ' (' + item.num + ')' + '</a></li>');
      $li.appendTo('#categories');
    });
    $('#categories').append("<li><a class='nav-link category' id=0>Uncategorized (" + json.uncategorized + ')' + '</a></li>');
  });
};
function my_bookmarks(category_id = -1) {
  var param;
  if (category_id == -1) {
    param = '';
  } else {
    param = '?category=' + category_id;
  };
  $.get('/bookmark' + param, function (html) {
    $('.content').html(html);
  }).done(function () {
    document.title = $('.title').text() + ' - My Bookmarks';
  });
  $('.category').removeClass('active');
  $('#' + category_id).addClass('active');
};
function category(category_id = 0) {
  var url, title;
  if (category_id == 0) {
    url = '/category/add';
    title = 'Add Category';
    if ($(window).width() <= 900) {
      $('.sidebar').toggle('slide');
    };
  } else {
    url = '/category/edit/' + category_id;
    title = 'Edit Category';
  };
  $.get(url, function (html) {
    $('.content').html(html);
  }).done(function () {
    document.title = title + ' - My Bookmarks';
  });
};
function bookmark(id = 0, category_id = 0) {
  var url, title;
  if (id == 0) {
    if (category_id > 0) {
      url = '/bookmark/add?category_id=' + category_id;
    } else {
      url = '/bookmark/add';
    };
    title = 'Add Bookmark';
  } else {
    url = '/bookmark/edit/' + id;
    title = 'Edit Bookmark';
  };
  $.get(url, function (html) {
    $('.content').html(html);
  }).done(function () {
    document.title = title + ' - My Bookmarks';
  });
};
function setting() {
  $.get('/auth/setting', function (html) {
    $('.content').html(html);
  }).done(function () {
    document.title = 'Setting - My Bookmarks';
  });
};
function simplify_url() {
  if (isMobile.matches) {
    $('.url').each(function () {
      $(this).text($(this).text().replace(/https?:\/\/(www\.)?/i, ''));
    });
  } else {
    $('.url').each(function () {
      $(this).text($(this).attr('href'));
    });
  };
};
function goback() {
  var last = document.cookie.split('LastVisit=')[1];
  my_bookmarks(last);
};
