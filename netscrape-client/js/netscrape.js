var form = new FormData();
form.append("name", "my-name");
form.append("function", "output = \"test\"");
form.append("next", "0");
form.append("every", "1000");
form.append("times", "-1");
form.append("save", "true");
form.append("schema", "true");

var settings = {
  "async": true,
  "crossDomain": true,
  "url": "http://localhost:5000/schedule",
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
