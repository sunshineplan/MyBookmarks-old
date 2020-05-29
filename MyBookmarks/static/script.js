function load(category_id = null) {
  if (category_id === null) {
    category_id = document.cookie.split('LastVisit=')[1];
  }
  $.getJSON('/category/get', json => {
    $('#category-list').empty();
    $('#categories').empty();
    $('#-1.category').text('All Bookmarks (' + json.total + ')');
    $.each(json.categories, (i, item) => {
      $('#category-list').append($('<option>').prop('value', item.category));
      var $li = $("<li><a class='nav-link category' id='" + item.id + "'>" + item.category + ' (' + item.num + ')' + '</a></li>');
      $li.appendTo('#categories');
    });
    $('#categories').append("<li><a class='nav-link category' id=0>Uncategorized (" + json.uncategorized + ')' + '</a></li>');
  }).done(() => my_bookmarks(category_id));
};
function my_bookmarks(category_id = -1) {
  var param;
  if (category_id == -1) {
    param = '';
  } else {
    param = '?category=' + category_id;
  };
  fetch('/bookmark' + param).then(response => {
    if (response.redirected) {
      window.location = '/auth/login';
      return;
    } else {
      return response.text();
    };
  }).then(html => {
    $('.content').html(html);
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
  $.get(url, html => $('.content').html(html))
    .done(() => { document.title = title + ' - My Bookmarks'; $('#category').focus() });
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
  $.get(url, html => $('.content').html(html))
    .done(() => { document.title = title + ' - My Bookmarks'; $('#bookmark').focus() });
};
function setting() {
  $.get('/auth/setting', html => $('.content').html(html))
    .done(() => { document.title = 'Setting - My Bookmarks'; $('#password').focus() });
};
function doCategory(id) {
  var url;
  if (id == 0) {
    url = '/category/add';
  } else {
    url = '/category/edit/' + id;
  }
  $.post(url, $('input').serialize(), json => {
    if (json.status == 0) {
      swal('Error', json.message, 'error').then(() => {
        if (json.error == 1) {
          $('#category').val('');
        };
      });
    } else {
      load();
    };
  });
};
function doBookmark(id) {
  var url;
  if (id == 0) {
    url = '/bookmark/add';
  } else {
    url = '/bookmark/edit/' + id;
  }
  $.post(url, $('input').serialize(), json => {
    if (json.status == 0) {
      swal('Error', json.message, 'error').then(() => {
        if (json.error == 1) {
          $('#bookmark').val('');
        } else if (json.error == 2) {
          $('#url').val('');
        } else if (json.error == 3) {
          $('#category').val('');
        };
      });
    } else {
      load();
    };
  });
};
function doDelete(mode, id) {
  var url;
  if (mode == 'category') {
    url = '/category/delete/' + id;
  } else if (mode == 'bookmark') {
    url = '/bookmark/delete/' + id;
  } else {
    return false;
  };
  swal('Are you sure?', 'This ' + mode + ' will be deleted permanently.', 'warning', {
    buttons: true,
    dangerMode: true,
  }).then(confirm => {
    if (confirm) {
      $.post(url, json => {
        if (json.status == 1) {
          if (mode == 'bookmark') load(); else load(-1);
        };
      });
    };
  });
};
function doSetting() {
  $.post('/auth/setting', $('input').serialize(), json => {
    if (json.status == 1) {
      swal('Success', 'Your password has changed. Please Re-login!', 'success')
        .then(() => window.location = '/auth/login');
    } else {
      swal('Error', json.message, 'error').then(() => {
        if (json.error == 1) {
          $('#password').val('');
        } else if (json.error == 2) {
          $('#password1').val('');
          $('#password2').val('');
        };
      });
    };
  });
};
function simplify_url() {
  if (isMobile.matches) {
    $('.url').each(function () { $(this).text($(this).text().replace(/https?:\/\/(www\.)?/i, '')) });
  } else {
    $('.url').each(function () { $(this).text($(this).attr('href')) });
  };
};
function goback() {
  var last = document.cookie.split('LastVisit=')[1];
  my_bookmarks(last);
};
