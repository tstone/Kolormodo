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

// Python style getattr
var getattr = function(dict, attr, deflt) {
    try
    {
        return dict[attr]
    }
    catch (e) { }
    return deflt;
}

// *** Main theme browser ***********************************************************************************************
var ThemeBrowser = function() {
  var $tb = null;
  var $displayRows = 2;
  var $leftBuffer = [];
  var $middleBuffer = [];
  var $rightBuffer = [];
  var $langTemplate = '';

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
                ThemeBrowser.setBrowserHeight(function() {
                    ThemeBrowser.updateThemeView();
                });
            }, 250);
        });

        // Hashed address handling
        $.address.externalChange(function(event) {
            log('change');
            var pathNames = $.address.pathNames();
            var view = pathNames[0];

            switch(view) {
                case 'theme':
                    break;
                case 'browse':
                    var count = pathNames[2] || ($displayRows * 3);
                    if ($middleBuffer.length > 0) {
                        ThemeBrowser.setAtThemeId(pathNames[1], count);
                    }
                    else {
                        ThemeBrowser.fetchThemeData({ startWith: pathNames[1], displayCount: count});
                    }
                    break;
                default:
                    ThemeBrowser.fetchThemeData();
                    break;
            }
        });
    },
    setBrowserHeight: function(callback) {
        callback = callback || function(){};
        var vpheight = $(window).height();
        log('viewport height: ' + vpheight);

        var afterHeightAdjust = function() {
            // If we have data in the buffer, adjust it based on our amount of display rows
            if ($middleBuffer.length > 0) {
                var perPage = $displayRows * 3;
                if ($middleBuffer.length > perPage) {            // Too big
                    var diff = $middleBuffer.length - perPage;
                    for (var i=0; i<diff; i++) {
                        $rightBuffer.unshift($middleBuffer.pop());
                    }
                }
                else if ($middleBuffer.length < perPage) {       // Too small
                    var diff = perPage - $middleBuffer.length;
                    var counter = 0;
                    while (counter < diff && $rightBuffer.length > 0) {
                        $middleBuffer.push($rightBuffer.shift());
                        counter++;
                    }
                    if (counter < perPage) {
                        while(counter < diff && $leftBuffer.length > 0) {
                            $middleBuffer.push($leftBuffer.pop());
                            counter++;
                        }
                    }
                }
            }

            ThemeBrowser.updateThemeView(function() {
                // Re-show arrows if there is more data
                if ($rightBuffer.length > 0 || $leftBuffer.length > 0) {
                    ThemeBrowser.showControlArrows(callback);
                }
                else {
                    callback();
                }
            });
        }

        // 884 = body min-height (716) + theme-preview height (168)
        if (vpheight >= 884) {
            ThemeBrowser.hideControlArrows(function() {
                $displayRows = 3;
                $tb.parent().addClass('three-row');
                afterHeightAdjust();
            });
        }
        else {
            ThemeBrowser.hideControlArrows(function() {
                $displayRows = 2;
                $tb.parent().removeClass('three-row');
                afterHeightAdjust();
            });
        }
    },
    updateBrowseAddress: function() {
        var currTheme = $($tb.find('article').get(0)).attr('id').substring(3);
        $.address.path('/browse/' + currTheme + '/' + $middleBuffer.length);
    },
    leftArrowClick: function() {
        ThemeBrowser.shiftLeft(function() {
            ThemeBrowser.updateBrowseAddress();
        });
        return false;
    },
    rightArrowClick: function() {
        ThemeBrowser.shiftRight(function() {
            ThemeBrowser.updateBrowseAddress();
        });
        return false;
    },
    hideControlArrows: function(callback) {
        callback = callback || function(){};
        $('#arrow-left').clearQueue().fadeOut(750);
        $('#arrow-right').clearQueue().fadeOut(750, callback);
    },
    showControlArrows: function(callback) {
        callback = callback || function(){};
        $('#arrow-left').clearQueue().fadeIn(750);
        $('#arrow-right').clearQueue().fadeIn(750, callback);
    },
    fetchThemeData: function(params) {
        params = params || {};
        $.extend(true, {
            startWith: -1,
            displayCount: ($displayRows * 3),
            callback: function() {}
        }, params);

        log('Fetching theme data from server...');
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
                    // Set start
                    if (params.startWith > 0) {
                        ThemeBrowser.setAtThemeId(params.startWith, params.displayCount, params.callback, data.schemes);
                    }
                    else {
                        ThemeBrowser.setAtThemeId(data.schemes[0].id, params.displayCount, params.callback, data.schemes);
                    }
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
    hideThemeView: function(callback) {
        callback = callback || function(){};
        $tb.fadeOut(150, callback);
    },
    showThemeView: function(callback) {
        callback = callback || function(){};
        $tb.fadeIn(150,callback);
    },
    isThemeViewVisible: function() {
        return !$tb.css('display', 'none');
    },
    updateThemeView: function(callback) {
        callback = callback || function(){}
        var doUpdate = function() {
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
            if ($leftBuffer.length === 0 && $rightBuffer.length === 0) {
                ThemeBrowser.hideControlArrows();
            }
            else {
                ThemeBrowser.showControlArrows();
            }
            // Activate hover effects
            $('.themes .theme-preview').hoverClass('theme-preview-hover');
            // Fade back in
            ThemeBrowser.showThemeView(callback);
        }
        if (ThemeBrowser.isThemeViewVisible()) {
            ThemeBrowser.hideThemeView(doUpdate);
        }
        else {
            doUpdate();
        }
    },
    setAtThemeId: function(themeId, displayCount, callback, values) {
        // themeId -- where to start
        // Values (optional) -- array of values to use
        log('setting to theme Id #' + themeId);
        themeId = Number(themeId || 0);
        displayCount = displayCount || ($displayRows * 3);
        callback = callback || function(){};
        values = values || [];

        // If values aren't given, concat our 3 buffers together and use those
        if (values.length === 0) {
            values = $leftBuffer.concat($middleBuffer, $rightBuffer);
            $leftBuffer = [];
            $middleBuffer = [];
            $rightBuffer = [];
        }
        // Set left
        while (values.length > 0) {
            if (Number(values[0].id) === themeId) { break; }
            $leftBuffer.push(values.shift());
        }
        // Set middle & right
        //var perPage = Number($displayRows * 3);
        perPage = displayCount;
        if(values.length >= perPage) {
            $middleBuffer = values.slice(0, perPage);
            $rightBuffer = values.slice(perPage);
        }
        else {
            $middleBuffer = values;
            var diff = perPage - $middleBuffer.length;
            var offset = $leftBuffer.length - diff;
            $middleBuffer = $middleBuffer.concat($leftBuffer.slice(offset).reverse());
            $leftBuffer = $leftBuffer.slice(0,offset);
        }
        // Display
        ThemeBrowser.updateThemeView(callback);
    },
    shiftRight: function(callback) {
        callback = callback || function(){}
        if ($rightBuffer.length > 0) {
            // Middle -> Left
            ThemeBrowser.shift($middleBuffer, $leftBuffer);
            // Right -> Middle
            ThemeBrowser.shift($rightBuffer, $middleBuffer, true);
        }
        else {
            ThemeBrowser.reverseShift($leftBuffer, $rightBuffer);
            ThemeBrowser.shiftRight();
            //$pagingOffset = 0;
        }
        ThemeBrowser.updateThemeView(callback);
    },
    shiftLeft: function(callback) {
        callback = callback || function(){}
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
        ThemeBrowser.updateThemeView(callback);
    },
    safeShiftLength: function(src, dest, safelen) {
        var count = 0;
        if (typeof(safelen) !== 'undefined') {
            if (safelen) {
                count = $displayRows * 3;
                if (src.length < count) {
                    count = src.length;
                }
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