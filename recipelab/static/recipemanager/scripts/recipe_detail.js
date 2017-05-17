var edit_panel_open;
var last_display;
var display = $('#recipe-display');

$(document).ready(function() {
    edit_panel_open = false;
    $('#hist-v-'+get_current_version()).addClass('active-version')
});

// Load version from history if clicked
$("#version-history").on('click', "li", function () {
    var new_version = this.id.split('-')[2];
    $('#version-history').children().removeClass('active-version');
    $(this).addClass('active-version');
    if (edit_panel_open) {
        get_version_data(new_version,  update_recipe_display);
    }
    else {
        get_version_data(new_version,  update_recipe_display,"plain");
    }
});

// save a revision to current version
$("#edit-save").on('click', function(){
    save_version_data(get_current_version(), "revise", update_recipe_display);
    close_edit_panel();
});

// save as a new version
$("#edit-new-version").on('click', function(){
    // create the new version in the database
    // change the page to the new version
    // update the history panel
    // show new version in edit mode

    save_version_data(get_current_version(), 'as-new-version', new_version);

});

// save as new recipe
$("#edit-new-recipe").on('click',function (){
    save_version_data(get_current_version(),'as-new-recipe', update_recipe_display)
    close_edit_panel()
});

// enter edit mode and show edit buttons
$("#edit-toggle").click(function () {
    if (!edit_panel_open){
        open_edit_panel();
        get_version_data(get_current_version(), update_recipe_display);
    } else {
        // edit is canceled
        console.log('Edit Cancelled')
        close_edit_panel();
        update_recipe_display(last_display);
    }
});

function get_current_version() {

    var version_id = $('.active-version').attr('id');
    console.log(version_id);
    return version_id.split('-')[2]
    // return $('#version_id').text();
}

function set_current_version(v_id) {
    $('version_id').text(v_id)
}

// open edit buttons panel
function open_edit_panel() {
    var icon = $("#edit-icon");
    icon.removeClass('glyphicon-pencil');
    icon.addClass('glyphicon-ban-circle');
    $(".edit-hidden").show();
    edit_panel_open = true;
}

// close edit buttons panel
function close_edit_panel (){
    var icon = $("#edit-icon");
    icon.removeClass('glyphicon-ban-circle');
    icon.addClass('glyphicon-pencil');
    $('.edit-hidden').hide();
    edit_panel_open = false;
}

// Retrieve recipe information via ajax
function get_version_data(version_id, response_handler, return_type) {

     $.ajax({
        url : "convertform/",
        type : "GET",
        data : { version : version_id,
            return_type: return_type},

        success : function(rdata){
            response_handler(rdata);
        },
        error : function(xhr, errmsg, err) {
            console.log(errmsg + ": " + xhr.status + ": " + xhr.responseText)
        }
    });
}

// save recipe information via ajax
function save_version_data(version_id, type, response_handler) {

    $.ajax({
        url : 'convertform/',
        type : "POST",
        data : { version: version_id,
            item_data: $('#item-form').val(),
            method_data: $('#method-form').val(),
            change_note: $('#change-note-form').val(),
            result_note: $('#result-note-form').val(),
            general_note: $('#general-note-form').val(),
            save_type: type},

        success: function(rdata){

            response_handler(rdata);
        },
        error : function(xhr, errmsg, err) {
            console.log(errmsg + ": " + xhr.status + ": " + xhr.responseText)
        }
    });
}

function new_version (json) {
    console.log("New Version");
    // update the version to the current version
    $('#version_id').text(json.version_id);
    console.log("Current Version: " + get_current_version());

    $('#version-history').children().removeClass('active-version');
    // add new entry to the history list as active version
    var new_list_item = '<li class="history-item active-version" id="hist-v-'+json.version_id+'">'+json.version_num+': '+json.date_created+'- ID: '+json.version_id+'</li>';
    console.log(new_list_item);
    $('#version-history').prepend(new_list_item);
    // update the display with the new display
    update_recipe_display(json);
}

function update_recipe_display(json) {
    console.log('Updating recipe display');
    last_display = display.html();
    var new_display;

    new_display = json.new_display;

    if (new_display == undefined) {
        new_display = json;
    }

    display.html(new_display);
}
