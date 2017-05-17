$(document).ready(function () {
    console.log("Cookie: "+document.cookie);
    console.log("Host: "+document.location.host);
    console.log("protocol: "+document.location.protocol);
});

$('#add-recipe').on('click', function () {

    $('#new-recipe-container').show();
    console.log('form was created');
    $('#add-recipe').hide();
});

$('#new-recipe-form').on('submit', function (event) {
   event.preventDefault();
   console.log('form was submitted');
   create_recipe();
});

$('#srch-term').on('input', function () {
    console.log('I tried to filter the list!')
    search_recipe_list($(this).val(), 'html', filter_list);
});

function filter_list(rdata){
    $('#recipe-list').html(rdata.html)
}

function create_recipe () {
    console.log("creating a new recipe");
    $.ajax({
        url: "newrecipe/",
        type: "POST",
        data: { recipe_name: $('#new-recipe-name').val()},

        success: function(jsondata){
            console.log('new recipe was made: '+jsondata.recipe_name);

            // clear and hide the from
            $('#new-recipe-name').val('');
            $('#new-recipe-container').hide();
            $('#add-recipe').show();


            // add a new recipe to the recipe-list
            $('#recipe-list').prepend(jsondata.recipe_html)

        },
        error: function(xhr, errmsg, err){
            console.log('An error occurred');
        }
        }

    )
}