
function getParameterByName(name, url)
{
  url = url || window.location.href;
  name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
  var regexS = "[\\?&]"+name+"=([^&#]*)";
  var regex = new RegExp(regexS);
  var results = regex.exec(url);
  if(results == null)
    return "";
  else
    return decodeURIComponent(results[1].replace(/\+/g, " "));
}

function removeParameterFromUrl(name, url) {
    var val = getParameterByName(name, url);
    return url.replace(name + '=' + val, '').replace('&&', '');
}

var detailsOnHover = function() {
    $('.schemes div.scheme').hover(
        function() {
            $(this).find('div.details').stop(true, true).fadeIn(450);
        },
        function() {
            $(this).find('div.details').stop(true, true).fadeOut(450);
        }
    );
}

var $langs = {};
var $lang_changes = 0;
var $langs_preloaded = false;
var $line_nums = '<div class="ksf-linenumbers"><span>1.</span><span>2.</span><span>3.</span><span>4.</span><span>5.</span><span>6.</span><span>7.</span><span>8.</span><span>9.</span><span>10.</span><span>11.</span><span>12.</span><span>13.</span><span>14.</span><span>15.</span></div>';

var setLangTemplate = function(lang, html) {
    $('article .ksf-common').each(function() {
        $(this).attr('class', 'ksf-common ' + lang).html(html);
    });
    // Update links (if present)
    $('nav.schemes ul li a, .pagination a,.schemes a.clickable').each(function() {
        var url = $(this).attr('href');
        url = removeParameterFromUrl('lang', url).replace('&&', '');
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
                callback($line_nums + html, lang);
            }
        }
    });
}

var storeInTemplateLang = function(elem, lang) {
    elem = $($(elem).clone())
    elem.find('.ksf-linenumbers').remove();
    var html = $line_nums + elem.html();
    if (Modernizr.localstorage) {
        log('Storing ' + lang);
        localStorage.setItem(lang + '_template', html);
        localStorage.setItem(lang + '_template_timestamp', (new Date()).getTime());
    }
    else {
        $langs[lang] = html;
    }
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
    var select = $('#main .lang select');

    // Rectify querystring with select val
    var lang = getParameterByName('lang') || "";
    if (lang.length > 0) {
        $('#main .lang select').val(lang);
    }

    var defaultBtn = $('#main .lang .default');
    defaultBtn.click(function() {
        $.ajax({
            url: '/user/set/lang',
            data: { lang: select.val() },
            type: 'GET',
            success: function() {
                defaultBtn.text('Lang Set');
                setTimeout(function() {
                    defaultBtn.text('Default');
                }, 5000);
            },
            error: function() {
                alert('A server error prevented your default language from being set.  Try again later.');
            }
        });
        return false;
    });

    select.change(function() {
        var val = select.val() || "";
        $lang_changes += 1;

        // Check if the template is already in cache
        if (val.length > 0) {
            if (defaultBtn.css('display') == 'none') {
                defaultBtn.fadeIn(500);
            }

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
        else {
            if (defaultBtn.css('display') != 'none') {
                defaultBtn.fadeOut(500);
            }
        }

    });
}

// Modified version of sohtanka.com Simple Tabs
// http://www.sohtanaka.com/web-design/simple-tabs-w-css-jquery/
var SimpleTabs = function(tabs, container) {
    container.children().hide();
    tabs.find('li:first').addClass("active").show();
    container.find('div:first').show();

    var lis = tabs.find('li');
    lis.click(function() {
        lis.removeClass("active");
        $(this).addClass("active");
        container.children().hide();

        var activeTab = $(this).find("a").attr("href");
        $(activeTab).fadeIn(350);
        return false;
    });
};

var GitHubUI = function(parent) {
    var input = parent.find('.name input');
    var select = parent.find('.gists select');
    var gisttext = parent.find('textarea');

    var getGists = function() {
        var name = input.val();
        if (typeof(name) !== 'undefined' && name.length > 0) {
            input.addClass('ajax-loading');
            $.getJSON('http://gist.github.com/api/v1/json/gists/' + name + '?callback=?', function(data){
                input.removeClass('ajax-loading');
                if (typeof(data.gists) !== 'undefined') {
                    select.children().remove();
                    select.append('<option value="">Choose a Gist</option>');
                    $.each(data.gists, function(index, gist){
                        $.each(gist.files, function(i, file) {
                            $('<option />').attr('value', gist.repo).text(file).appendTo(select);
                        });
                    });
                    input.parent().fadeOut(250, function(){
                        select.parent().fadeIn(250);
                    });
                }
                else {
                    alert('That GitHub username was not found.');
                }
            });
        }
        else {
            alert('Please enter your GitHub username first');
        }
    };

    parent.find('#find-gists-btn').click(function() { getGists(); });
    input.keypress(function(e){
        if (e.keyCode == 13 || e.which == 13 ) {
            getGists();
            return false;
        }
    });

    select.change(function() {
        var url = '/github/get-gist/' + select.val() +'/' + select.find(':selected').text();
        parent.find('#ajax-loading').show();
        $.get(url, function(data){
            gisttext.val(data);
            gisttext.parent().fadeIn(250);
            parent.find('#ajax-loading').hide();
        });
    });
};

// *** Document Ready ***************************************************************************************************
$(function() {
    // Hello, world!
});
