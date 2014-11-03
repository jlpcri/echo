/**
 * Created by sliu on 11/3/14.
 */

/* make folders collapsible */
function makeCollapsible() {
    // Find list items representing folders and
    // style them accordingly.  Also, turn them
    // into links that can expand/collapse the
    // tree leaf.
    $('li > ul').each(function (i) {
        // Find this list's parent list item.
        var parent_li = $(this).parent('li');

        // Style the list item as folder.
        parent_li.addClass('folder');

        // Temporarily remove the list from the
        // parent list item, wrap the remaining
        // text in an anchor, then reattach it.
        var sub_ul = $(this).remove();
        parent_li.wrapInner('<a/>').find('a').click(function () {
            // Make the anchor toggle the leaf display.
            sub_ul.toggle();
            if ($(sub_ul).is(":hidden")) {
                $("#missing_slots_view").removeClass('fa-minus-square-o');
                $("#missing_slots_view").addClass('fa-plus-square-o');
            } else {
                $("#missing_slots_view").removeClass('fa-plus-square-o');
                $("#missing_slots_view").addClass('fa-minus-square-o');
            }
        });
        parent_li.append(sub_ul);
    });

    // Hide all lists except the outermost.
    $('ul ul').hide();
}

$(document).ready(function () {
    makeCollapsible();
});