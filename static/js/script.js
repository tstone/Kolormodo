
function getParameterByName(name)
{
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp( regexS );
  var results = regex.exec( window.location.href );
  if( results == null )
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}

function removeParameterFromUrl(name, url) {
    var val = getParameterByName(name);
    return url.replace(name + '=' + val, '');
}

var setActiveSortTab = function() {
    // Determine sort
    var m = ((/\?[^&]*s=([^&]+|^)/).exec(window.location.href) || ['',''])[1]
    if (m.length > 0) {
        $('#sort-' + m).addClass('active');
    }
    else {
        $('#sort-new').addClass('active');
    }
}

var $langs = {};
var $lang_changes = 0;
var $langs_preloaded = false;

var setLangTemplate = function(lang, html) {
    $('article .ksf-common').each(function() {
        $(this).html(html);
    });
    // TODO: Update pagination querystrings
    // Update links (if present)
    $('nav.schemes ul li a, .pagination a').each(function() {
        var url = $(this).attr('href');
        url = removeParameterFromUrl('lang', url);
        $(this).attr('href', url + '&lang=' + lang);
    });
}

var fetchLangTemplate = function(lang, callback) {
    var html = '';
    $.ajax({
        url: '/api/get-template',
        data: { lang: lang },
        type: 'GET',
        success: function(data, status, xhr) {
            html = data;
        },
        error: function(data, status, xhr) {
            alert("A server error has prevented the " + lang + " view from being displayed.");
        },
        complete: function() {
            if (typeof(callback) == 'function') {
                callback(html, lang);
            }
        }
    });
}

var checkLangLocalstorage = function(lang) {
    var updateLangLS = function(lang, html) {
        setLangTemplate(lang, html);
        localStorage.setItem(lang + '_template', html);
        localStorage.setItem(lang + '_template_timestamp', (new Date()).getTime());
    };

    var html = localStorage.getItem(lang + '_template');
    if ((html || "").length > 0) {
        // Check timestamp (in milliseconds) to make sure it's not too old
        var timestamp = localStorage.getItem(lang + '_template_timestamp');
        if ((new Date()).getTime() < (timestamp + 2592000000)) {   // 30 day cache
            log('Loading template from local storage...');
            setLangTemplate(lang, html);
            return;
        }
        else {
            log('Local storage out of date...');
            fetchLangTemplate(lang, function(html, lang){
                updateLangLS(lang, html);
            });
            return;
        }
    }
    else {
        log('Local supported by not present');
        fetchLangTemplate(lang, function(html, lang){
            updateLangLS(lang, html);
        });
        return;
    }
}

var activatePreviewLanguage = function() {

    $('#main .lang select').change(function() {
        var select = $(this);
        var val = select.val() || "";
        $lang_changes += 1;

        // Check if the template is already in cache
        if (val.length > 0) {
            if (($langs[val] || "").length > 0) {
                setLangTemplate(val, $langs[val]);
                return;
            }
            // Check if it's in HTML5 local storage
            if (Modernizr.localstorage) {
                checkLangLocalstorage(val);
                return;
            }
            // If not fetch it from the server
            fetchLangTemplate(val, function(html) {
                setLangTemplate(val, html);
            });
        }
    });
}


// *** Document Ready ***************************************************************************************************
$(function() {


});