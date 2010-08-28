window.log = function(){
  // Only show log when in local development
  if (window.location.href.indexOf('http://local') == 0) {
    log.history = log.history || [];
    log.history.push(arguments);
    if(this.console){
      console.log( Array.prototype.slice.call(arguments) );
    }
    else{
      alert(arguments);
    }
  }
};

// jQuery Plugin for simple hover class swapping
$.fn.hoverClass = function(cssClass) {
  $(this).each(function() {
    $(this).hover( function() { $(this).addClass(cssClass); }, function() { $(this).removeClass(cssClass); } );
  });
  return this;
};

// jQuery Plugin for simple hover class swapping
$.fn.parentHoverClass = function(cssClass) {
  $(this).each(function() {
    $(this).hover( function() { $(this).parent().addClass(cssClass); }, function() { $(this).parent().removeClass(cssClass); } );
  });
  return this;
};

// jQuery Plugin for simple hover/mousedown/mouseup class swapping
$.fn.buttonBehavior = function(hoverClass, downClass) {
  $(this).each(function() {
    $(this).hoverClass(hoverClass).mousedown(function() { $(this).addClass(downClass); }).mouseup(function() { $(this).removeClass(downClass); });
    $(this).click(function(){ $(this).blur(); });
  });
  return this;
};

/*
(function(doc){
  var write = doc.write;
  doc.write = function(q){
    log('document.write(): ',arguments);
    if (/docwriteregexwhitelist/.test(q)) write.apply(doc,arguments);
  };
})(document);
*/
