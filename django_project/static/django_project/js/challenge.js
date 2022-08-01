var password_id_to_retrieve = -1;

var unique_number = -1;
var instances_of_number = 0;
var number_of_lines = 0;
var number_of_solves = 0;
var password_name = "";

var domain = "https://app.thepasslock.com/";
// -------------------------------------------------------------------------
// Disable Ctrl + F to find the numbers in challenge.
// -------------------------------------------------------------------------
$(window).keydown(function(e){
    if ((e.ctrlKey || e.metaKey) && e.keyCode === 70) {
        e.preventDefault();
    }
});
// -------------------------------------------------------------------------
$('.password').click(function(e) {
    resetVariables();
    var challenge_time = $(this).attr('time');
    password_id_to_retrieve = $(this).attr('passID');
    password_name = $(this).attr('name');
    // Takes 30s per line, challenge time is in minutes
    number_of_lines = challenge_time * 2;
    generateLine();
    $("#solution").focus();
});
// -------------------------------------------------------------------------
function generateLine() {
    // Generate a unique number
    unique_number = Math.floor(Math.random() * 10);

    // Generate a bunch of numbers.
    var numbers = [...Array(50)].map(() => Math.floor(Math.random() * 10))

    // Count the number of occurences of the unique number.
    instances_of_number = 0;
    for(var j=0; j < numbers.length; j++) {
      if(numbers[j] == unique_number) {
        instances_of_number += 1;
      }
    }
    setup_modal(numbers);
}
// -------------------------------------------------------------------------
function setup_modal(numbers) {
  $('#unique-number').html(unique_number);
  var numberString = "<div class='row'>";
  for(var i=0; i < numbers.length; i++) {
    numberString += "<div class='col-1'>" + numbers[i] + "</div>";
  }
  numberString += "</div>";
  $('#number-sequence').html(numberString);
  $('#challenge-modal').modal();
  $('#password-name').html("Retrieve " + password_name);
  updateProgressBar();
}
// -------------------------------------------------------------------------
$(document).on('keypress',function(e) {
    if(e.which == 13) {
        handle_submission();
    }
});
// -------------------------------------------------------------------------
 $(document).on('click','#submit-solution',function(){
   handle_submission();
});
// -------------------------------------------------------------------------
function handle_submission() {
  var solution = $("#solution").val();

  if((solution != "") && (solution == instances_of_number)) { // Check for correct answer
      number_of_solves += 1;
      $('#error-text').html("");

      if(number_of_lines == number_of_solves) { // Check for completion
        retreievePassword();
        instances_of_number = 0; // Reset all variables
        number_of_lines = 0;
        number_of_solves = 0;
        resetSolutionValue();
      }
      else {
        generateLine();
        resetSolutionValue();
        $("#solution").focus();
      }
  } else { // Let user know that their answer was incorrect
    if(number_of_solves > 0) {
      number_of_solves -= 1;
    }
    $('#error-text').html("Incorrect, try again!<br/>");
    generateLine();
    resetSolutionValue();
    $("#solution").focus();
  }
  updateProgressBar();
}
// -------------------------------------------------------------------------
function updateProgressBar() {
  progress = (number_of_solves/number_of_lines);
  if(isNaN(progress)) {
    $('#progress').html("Solves: 0 / " + number_of_lines);
  }
  else {
    $('#progress').html("Solves: " + number_of_solves + " / " + number_of_lines);
  }
}
// -------------------------------------------------------------------------
function retreievePassword() {
  _mfq.push(["stop"]);
  var url = domain + "passwords/retrieve-password/" + password_id_to_retrieve;
  $.ajax({
      url: url,
      type: "GET",
      statusCode: {
          403: function(data) {
            alert(data['responseJSON']['error']);
          },
          200: function(data) {
            $('#challenge-body').html("<br><h6>Username: </h6>" + data['username'] + "<br><br><h6>Password: </h6>" + data['password']);
            $('#progress').css('display', 'none');
            $('#warning').css('display', 'none');
          }
      }
  });
}
// -------------------------------------------------------------------------
function resetVariables() {
    instances_of_number = 0;
    number_of_lines = 0;
    number_of_solves = 0;
    resetSolutionValue();
    updateProgressBar();
}
// -------------------------------------------------------------------------
function resetSolutionValue() {
    $("#solution").val("");
}
// -------------------------------------------------------------------------
function reportFailedRetrieve() {
    url = domain + "passwords/report-failed-retrieve/" + password_id_to_retrieve + "/";
    $.post(url, function() {console.log("HERE")});
}
// -------------------------------------------------------------------------
$('#challenge-modal').on('hidden.bs.modal', function (e) {
    reportFailedRetrieve();
    window.location.reload();
})
// -------------------------------------------------------------------------
