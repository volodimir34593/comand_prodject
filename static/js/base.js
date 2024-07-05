document.addEventListener('DOMContentLoaded', function() {
  $('#searchForm').on('submit', function(event) {
    event.preventDefault();
    var searchQuery = $('#searchInput').val();
    if (searchQuery) {
      window.location.href = '/search?query=' + encodeURIComponent(searchQuery);
    }
  });
});
