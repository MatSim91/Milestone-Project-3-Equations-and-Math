
/* jQuery initialization for features from Materialize  */
$(document).ready(function(){
    $('.sidenav').sidenav();
    $('textarea#description').characterCounter();
    $('select').formSelect();
    $('.datepicker').datepicker({
      format: 'dd mmmm, yyyy',
      yearRange: [1300, 2000],
      showClearBtn: true,
      i18n: {
        done: 'Select'
      }
    });
  });