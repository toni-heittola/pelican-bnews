$(document).ready(function(){
    var timeagoInstance = timeago();
    var nodes = document.querySelectorAll('.bnews-time');
    timeagoInstance.render(nodes);
    timeago.cancel();
});