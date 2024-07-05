document.addEventListener('DOMContentLoaded', function() {
  $('#searchForm').on('submit', function(event) {
    event.preventDefault();
    search();
  });

  $('#category_id').on('change', function() {
    search();
  });

  $('#minPrice, #maxPrice').on('keyup', function(event) {
    if (event.key === 'Enter') {
      search();
    }
  });

  function search() {
    var searchQuery = $('#searchInput').val();
    var category = $('#category_id').val();
    var minPrice = $('#minPrice').val();
    var maxPrice = $('#maxPrice').val();
    var url = '/search?query=' + encodeURIComponent(searchQuery);
    
    // Check if category is not null or undefined, then add it to URL
    if (category != null && category !== undefined) {
      url += '&category_id=' + encodeURIComponent(category);
    }
    
    if (minPrice) {
      url += '&min_price=' + encodeURIComponent(minPrice);
    }
    if (maxPrice) {
      url += '&max_price=' + encodeURIComponent(maxPrice);
    }
    
    // Redirect to the formed URL
    window.location.href = url;
  }
});
