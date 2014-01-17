$(function(){
  function create_accordian(str) {
    $( str )
      .accordion({
        header: '> div > h3',
        autoHeight: false  // set this to false
      })
      .sortable({
        axis: 'y',
        handle: 'h3',
        stop: function( event, ui ) {
            // IE doesn't register the blur when sorting
            // so trigger focusout handlers to remove .ui-state-focus
            ui.item.children( 'h3' ).triggerHandler( 'focusout' );
        }
      });
  }
  create_accordian("#subpours_accord");
});
$(function() {
  timer = setInterval(function(){
    $.get("/status", function(data) { $(".status").html(data); });
  }, 1000);
});
