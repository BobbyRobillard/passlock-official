var admin_email = "admin@techandmech.com";
//------------------------------------------------------------------------------
// For items that direct a user somewhere. I.e: trashcan (delete), pencil (edit)
//------------------------------------------------------------------------------
$('body').on('click', '.action-link', function(e) {
    e.preventDefault();
    e.stopPropagation();
    $('.modal').each(function() {
      $(this).modal('hide');
    });
    window.location.href = $(this).attr('href');
});
//------------------------------------------------------------------------------
// Filtering Method
//------------------------------------------------------------------------------
function hideAddPassword() {
  $('.add-password-btn').css('display', 'none');
  $('.add-password-mobile').prop("disabled", true);
  $('.add-password-mobile').attr("title", "Add Password Currently Disabled!");
}
//------------------------------------------------------------------------------
// Add Password Functionality
//------------------------------------------------------------------------------
$('.add-password').click(function() {
  $('#add-password-modal').modal();
});
//------------------------------------------------------------------------------
// Instant Unlock Functionality
//------------------------------------------------------------------------------
var unlock_url = "";
$('.unlock').click(function(e) {
  e.stopPropagation();
  $('#unlock-modal').modal();
  $("#unlock-confirm-form").attr('action', $(this).attr('href'));
});
//------------------------------------------------------------------------------
// Credit Card Form Ease Of Use Functionality
//------------------------------------------------------------------------------
$('#id_number').bind('keypress', function(e) {
  var num = $(this).val();
  var stripped = num.replaceAll('-', '');
  if(stripped.length % 4 == 0) {
    if(stripped.length != 0 && stripped.length < 16) {
      $(this).val(num + "-");
    }
  }
});
//------------------------------------------------------------------------------
// Initialize Tooltips, Bootstrap 4
// https://www.w3schools.com/bootstrap4/bootstrap_tooltip.asp
//------------------------------------------------------ ------------------------
$('.terms').click(function() {
  $('#terms-modal').modal();
});
//------------------------------------------------------------------------------
// Initialize Tooltips, Bootstrap 4
// https://www.w3schools.com/bootstrap4/bootstrap_tooltip.asp
//------------------------------------------------------ ------------------------
$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});
