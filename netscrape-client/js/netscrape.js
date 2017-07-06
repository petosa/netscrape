var validateForm = function() {
  var name = document.getElementById("name").value
  var description = document.getElementById("description").value
  var runevery = document.getElementById("runevery").value
  var scale = document.getElementById("scale").value
  var code = document.getElementById("code").value
  var infinite = document.getElementById("infinite").checked
  var times = document.getElementById("times").value
  var save = document.getElementById("save").checked
  var schema = document.getElementById("schema").checked
  if (name != "" && runevery != "" && scale != "" && code != "" && (infinite || times)) {
    var form = new FormData();
    form.append("name", name);
    form.append("function", code);
    form.append("next", 0);
    form.append("every", runevery);
    form.append("times", infinite ? -1 : times);
    form.append("save", schema);
    form.append("schema", schema);
    sendForm()
  } else {
    console.log("No good.")
  }
  return false;
}


var sendForm = function(form) {
  var settings = {
    "async": true,
    "crossDomain": true,
    "url": "http://petosa.ddns.net:5002/schedule",
    "method": "PUT",
    "headers": {},
    "processData": false,
    "contentType": false,
    "mimeType": "multipart/form-data",
    "data": form
  }
  $.ajax(settings).done(function (response) {
    console.log(response);
  });
}
