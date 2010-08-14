var Filters = function() {
    var filtContainer = 'div.filters div.container';
    var filters_desc = [
        {
            title: 'General',
            filters: [
                {
                    value: 'c_lang',
                    text: 'Contains language colors for...',
                    sub_select: true,
                    sub_options: [
                        { value: 'c', text: 'C' },
                        { value: 'c++', text: 'C++' },
                        { value: 'c#', text: 'C#' },
                        { value: 'python', text: 'Python' }
                    ]
                },
                {
                    value: 'user',
                    text: 'Created by user (nickname)...',
                    sub_text: true
                },
                {
                    value: 'user_id',
                    text: 'Created by user (id)...',
                    sub_text: true
                },
                {
                    value: 'h_desc',
                    text: 'Has description'
                },
                {
                    value: 'c_title',
                    text: 'Title contains...',
                    sub_text: true
                },
                {
                    value: 'c_desc',
                    text: 'Description contains...',
                    sub_text: true
                }
            ]
        },
        {
            title: 'Color',
            filters: [
                {
                    value: 'c_color',
                    text: 'Contains main color...',
                    sub_color: true
                },
                {
                    value: 'h_light_bg',
                    text: 'Has light background'
                },
                {
                    value: 'h_med_bg',
                    text: 'Has medium background'
                },
                {
                    value: 'h_dark_bg',
                    text: 'Has dark background'
                }
            ]
        }
        /*
        {
            title: 'Popularity',
            filters: [
                ['views', 'Views...'],
                ['downloads', 'Downloads...'],
                ['upvotes', 'Up-votes...']
            ]
        },
        {
            title: 'Age',
            filters: [
                ['added', 'Added to site...'],
                ['updated', 'Last updated...'],
            ]
        }
        */
    ];

    return {
        init: function() {
            var startingPrimary = $(Filters.generatePrimarySelectMarkup());
            startingPrimary.find('select').change(Filters.onPrimaryChange);
            $(filtContainer).append(startingPrimary);
        },

        getFilterByValue: function(val) {
            var f = null;
            $.each(filters_desc, function(index, section) {
                $.each(section.filters, function(index, filter){
                    debug('|' + filter.value + '| == |' + val + '|');
                    if (filter.value == val) {
                        f = filter;
                    }
                });
            });
            return f;
        },

        generatePrimarySelectMarkup: function() {
            var opts = '<option value=""></option>';
            $.each(filters_desc, function(index, section) {
                opts += '<optgroup label="' + section.title + '">\n';
                $.each(section.filters, function(index, filter){
                    opts += '<option value="' + filter.value + '">' + filter.text + '</option>\n';
                });
                opts += '</optgroup>\n';
            });
            return '<div class="filter"><select class="primary">\n' + opts + '</select></div>\n';
        },

        onPrimaryChange: function() {
            var filter = Filters.getFilterByValue($(this).val());
            if (filter) {
                var parent = $(this).parent();
                var html = '';

                $(parent).find('.secondary').remove();
                $(parent).find('.tertiary').remove();

                if (filter.sub_select) {
                    html = '<option value=""></option>';
                    $.each(filter.sub_options, function(index, subfilter) {
                        html += '<option value="' + subfilter.value + '">' + subfilter.text + '</option>\n';
                    });
                    html = '<select class="secondary">\n' + html + '</select>\n';
                }
                else if (filter.sub_text) {
                    html = '<input type="text" class="secondary" value="" />';
                }

                $(parent).append(html);
            }
        }
    };
}();