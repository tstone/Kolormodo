var AjaxLoading = function() {
    return {
        show: function() {
            $('#ajax-loading').clearQueue().fadeIn(250);
        },
        hide: function() {
            $('#ajax-loading').clearQueue().fadeOut(250);
        }
    }
}();

// *** Main theme browser ***********************************************************************************************
var ThemeBrowser = function() {
  var $tb = null;
  var $displayRows = 2;
  var $leftBuffer = [];
  var $middleBuffer = [];
  var $rightBuffer = [];
  var $langTemplate = '';

  var columns = 3;
  var schemeTemplate = '';
  schemeTemplate += '<div class="theme-preview">\n';
  schemeTemplate += '   <style type="text/css">';
  schemeTemplate += '      %css%';
  schemeTemplate += '   </style>';
  schemeTemplate += '   <article id="cs-%id%">\n';
  schemeTemplate += '      <div class="ksf-common">';
  schemeTemplate += '         %lang-template%';
  schemeTemplate += '      </div>';
  schemeTemplate += '   </article>';
  schemeTemplate += '   <a href="#TODO" class="clickable-overlay" title="%title%"></a>';
  schemeTemplate += '</div>';

  return {
    init: function(elem) {
        log('ThemeBrowser initializing...');
        $tb = $(elem);
        $('#arrow-left a.left').click(ThemeBrowser.leftArrowClick);
        $('#arrow-right a.right').click(ThemeBrowser.rightArrowClick);

        ThemeBrowser.setBrowserHeight();
        $tb.css('width', $tb.width() + 'px');
        $tb.css('height', $tb.height() + 'px');

        // Adjust UI on resize
        var resizeTimer = null;
        $(window).resize(function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                ThemeBrowser.setBrowserHeight();
                ThemeBrowser.updateThemeView();
            }, 250);
        });

        ThemeBrowser.fetchThemeData();
    },
    setBrowserHeight: function(callback) {
        var vpheight = $(window).height();
        log('viewport height: ' + vpheight);

        // 884 = body min-height (716) + theme-preview height (168)
        if (vpheight >= 884) {
            $displayRows = 3;
            ThemeBrowser.hideControlArrows(function() {
                $tb.parent().addClass('three-row');
            });
        }
        else {
            $displayRows = 2;
            ThemeBrowser.hideControlArrows(function() {
                $tb.parent().removeClass('three-row');
            });
            // Calling this a 2nd time because of some wierd bug that causes it not to fire when
            // inside the hideControlArrows callback
            $tb.parent().removeClass('three-row');
        }
        // If we have data in the buffer, adjust it based on our amount of display rows
        if ($middleBuffer.length > 0)
        {
            var shouldbe = $displayRows * 3;
            if ($middleBuffer.length > shouldbe)
            {
                var diff = $middleBuffer.length - shouldbe;
                for (var i=$middleBuffer.length; i > shouldbe; i--)
                {
                    $rightBuffer.unshift($middleBuffer.pop());
                }
            }
            else if ($middleBuffer.length < shouldbe && $rightBuffer.length > 0)
            {
                var dff = shouldbe - $middleBuffer.length;
                for (var i=0; i < shouldbe; i++)
                {
                    if ($rightBuffer.length > 0)
                    {
                        $middleBuffer.push($rightBuffer.shift());
                    }
                }
            }
        }
        // Re-show arrows if there is more data
        if ($rightBuffer.length > 0 || $leftBuffer.length > 0)
        {
            ThemeBrowser.showControlArrows(callback);
        }
        else
        {
            if (typeof(callback) == 'function')
            {
                callback();
            }
        }
    },
    leftArrowClick: function() {
        ThemeBrowser.shiftLeft();
        return false;
    },
    rightArrowClick: function() {
        ThemeBrowser.shiftRight();
        return false;
    },
    hideControlArrows: function(callback) {
        $('#arrow-left').clearQueue().fadeOut(750);
        $('#arrow-right').clearQueue().fadeOut(750, callback);
    },
    showControlArrows: function(callback) {
        $('#arrow-left').clearQueue().fadeIn(750);
        $('#arrow-right').clearQueue().fadeIn(750, callback);
    },
    fetchThemeData: function() {
        AjaxLoading.show();
        $.ajax({
            type: 'GET',
            dataType: 'json',
            url: '/api/get-themes',
            data: {
                format: 'json',
                template: 'python'
            },
            success: function(data, status, xhr) {
                if (data.template) { $langTemplate = data.template; }
                if (data.schemes) {
                    var total = columns * $displayRows;
                    var inc = data.schemes;
                    if (inc.length > total) {
                        for (var i=0; i<total; i++) {
                            $middleBuffer.push(inc.shift());
                        }
                        var temp = inc.concat($rightBuffer);
                        $rightBuffer = temp;
                    }
                    else {
                        $middleBuffer = inc;
                    }
                    ThemeBrowser.updateThemeView();
                }
            },
            error: function(data, status, xhr) {
                alert("An error occured while fetching the color schemes.\nIt was probably... \nuh.... \num.... \n\n...I don't know.");
            },
            complete: function() {
                AjaxLoading.hide();
            }
        });
    },
    updateThemeView: function() {
        $tb.fadeOut(150, function() {
            // Build new elements
            $tb.children().remove();
            $.each($middleBuffer, function() {
                var scheme = this;
                var html = schemeTemplate;
                html = html.replace(/%id%/gi, scheme.id);
                html = html.replace(/%title%/gi, scheme.title);
                html = html.replace(/%lang-template%/gi, $langTemplate);
                html = html.replace(/%css%/gi, scheme.css);
                $tb.append(html);
            });
            // Adjust visibilty of arrow controls
            if ($leftBuffer.length == 0 && $rightBuffer.length == 0) {
                ThemeBrowser.hideControlArrows();
            }
            else {
                ThemeBrowser.showControlArrows();
            }
            // Activate hover effects
            $('.themes .theme-preview').hoverClass('theme-preview-hover');
            // Fade back in
            $tb.fadeIn(150);
        });
    },
    shiftRight: function() {
        if ($rightBuffer.length > 0) {
            // Middle -> Left
            ThemeBrowser.shift($middleBuffer, $leftBuffer);
            // Right -> Middle
            ThemeBrowser.shift($rightBuffer, $middleBuffer, true);
        }
        else {
            ThemeBrowser.reverseShift($leftBuffer, $rightBuffer);
            ThemeBrowser.shiftRight();
        }
        ThemeBrowser.updateThemeView();

    },
    shiftLeft: function() {
        if ($leftBuffer.length > 0) {
            // Middle -> Right
            ThemeBrowser.shift($middleBuffer, $rightBuffer);
            // Left -> Middle
            ThemeBrowser.shift($leftBuffer, $middleBuffer, true);
        }
        else {
            ThemeBrowser.reverseShift($rightBuffer, $leftBuffer);
            ThemeBrowser.shiftLeft();
        }
        ThemeBrowser.updateThemeView();
    },
    safeShiftLength: function(src, dest, safelen) {
        var count = 0;
        if (typeof(safelen) !== 'undefined') {
            if (safelen) {
                count = columns * $displayRows;
                if (src.length < count)
                    count = src.length;
            }
            else {
                count = src.length;
            }
        }
        else {
            count = src.length;
        }
        return count;
    },
    shift: function(src, dest, safelen) {
        var count = ThemeBrowser.safeShiftLength(src, dest, safelen);
        for(var i=0; i<count; i++) {
            dest.push(src.pop());
        }
    },
    reverseShift: function(src, dest, safelen) {
        var count = ThemeBrowser.safeShiftLength(src, dest, safelen);
        var buff = src.slice(count - (count * 2));
        for (var i = 0; i<count; i++) {
            dest.push(buff[i]);
            src.pop();
        }
    }
  };
}();
// jQuery wrapper for ThemeBrowser
$.fn.themeBrowser = function() {
  ThemeBrowser.init($(this).get(0));
  return ThemeBrowser;
};

// *** Document Ready ***************************************************************************************************
$(function() {

  // Enable button behavior
  $('nav').buttonBehavior('hover', 'down');
  $('.nav-arrow').buttonBehavior('nav-arrow-hover', 'nav-arrow-down');

  // Enable tooltips
  $('footer nav').tooltip();

});