


$(document).on("submit", "#external", function (e) {
        e.preventDefault();
    var Toast = Swal.mixin({
           toast: true,
           position: 'top-end',
           showConfirmButton: false,
           timer: 3000
    });
    if ( $('#assets').val().length > 0  && $('.company').val()!="" && $('#approver').val() != '' ) {

        $.ajax({
            type: 'POST',
            url: "/abcassetsmanager/external_transfers",
            data: {
                asset_tag: $('#assets').val(),
                company : $('.company').val(),
                assets : $('#assets').val(),
                approver: $('#approver').val(),
                reason: $("input[name='reason']:checked").val(),
                csrfmiddlewaretoken: $("input[name='csrfmiddlewaretoken']").val(),
                success: function(data){
                       Toast.fire({
                            icon: 'success',
                            title: 'Transaction Sent For Authorization',
                       })
                      $('#transaction').trigger("reset");
                      $("#user option").prop("selected", false).trigger( "change" );
                      $("#assets option").prop("selected", false).trigger( "change" );
                }
            }
        })
    } else {
        alert("Fill in missing fields")
    }
})





$(document).on("submit", "#company", function (e) {
    e.preventDefault();
    alert("company form submission");

})