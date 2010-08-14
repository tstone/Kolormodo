(function($) {

  // jQuery Plugin for simple hover class swapping
  $.fn.hoverClass = function(cssClass) {
    $(this).each(function() {
      $(this).hover( function() { $(this).addClass(cssClass); }, function() { $(this).removeClass(cssClass); } );
    });
    return this;
  };
  // jQuery Plugin for simple hover/mousedown/mouseup class swapping
  $.fn.buttonBehavior = function(hoverClass, downClass) {
    $(this).each(function() {
      $(this).hoverClass(hoverClass);
      $(this).mousedown(function() { $(this).addClass(downClass); }).mouseup(function() { $(this).removeClass(downClass) });
      // TODO: make this work properly
      $(this).click(function(){ $(this).blur(); });
    });
    return this;
  };

  // Main theme browser
  var ThemeBrowser = function() {
    return {
      init: function() {
        $('#left-arrow').click(ThemeBrowser.leftArrowClick);
        $('#right-arrow').click(ThemeBrowser.rightArrowClick);
      },
      leftArrowClick: function() {

      },
      rightArrowClick: function() {

      }
    }
  }();

  // *** Document Ready *******
  (function($){
    // Enable button behavior
    $('.themes .theme-preview').hoverClass('theme-preview-hover');
    $('nav').buttonBehavior('hover', 'down');
    $('.nav-arrow').buttonBehavior('nav-arrow-hover', 'nav-arrow-down');
    // Enable tooltips
  $('footer nav').tooltip();

    // ThemeBrowser if we're on home page (TODO: change to body.home)
    if ($('div.themes').length > 0) {
      ThemeBrowser.init();
    }
  })(window.jQuery);

})(jQuery);

window.log = function(){
  log.history = log.history || [];
  log.history.push(arguments);
  if(this.console){
    console.log( Array.prototype.slice.call(arguments) );
  }
};

(function(doc){
  var write = doc.write;
  doc.write = function(q){
    log('document.write(): ',arguments);
    if (/docwriteregexwhitelist/.test(q)) write.apply(doc,arguments);
  };
})(document);
