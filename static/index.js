$(document).ready(function() {

    // Show only canonical or all titles 
    var canon = "";
    $('#onlycanon').change(function(){
        if ($("#onlycanon").is(":checked")) {
            canon = "canon1";
        }
        else {
            canon = "";
        }
    });

    // Show only TVs
    $("#tvs").on("click", function() {
        $(".trow").each(function(){
            if ($(this).hasClass("TV" + canon)) {
                $(this).show();
            }
            else {
                $(this).hide();
            }})
    });

    // Show only movies 
    $("#movies").on("click", function() {
        $(".trow").each(function(){
            if ($(this).hasClass("Movie" + canon)) {
                $(this).show();
            }
            else {
                $(this).hide();
            }})
    });

    // Show only specials 
    $("#specials").on("click", function() {
        $(".trow").each(function(){
            if ($(this).hasClass("Special" + canon)) {
                $(this).show();
            }
            else {
                $(this).hide();
            }})
    });

    // Show only OVAs
    $("#ovas").on("click", function() {
        $(".trow").each(function(){
            if ($(this).hasClass("OVA" + canon)) {
                $(this).show();
            }
            else {
                $(this).hide();
            }})
    });
    
    // Show all
    $("#all").on("click", function() {
        if (canon === "") {
            $(".trow").show();
        }
        else {
            $(".trow").each(function(){
                if ($(this).hasClass(canon)) {
                    $(this).show();
                }
                else {
                    $(this).hide();
                }})}
    });
});
