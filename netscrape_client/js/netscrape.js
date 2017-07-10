var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("code"), {
    "theme": "icecoder"
});

var testFunction = function() {
    var code = myCodeMirror.getValue();
    if (code == "") {
        document.getElementById("failedMessage").innerHTML = "You must add a function before testing.";
        document.getElementById("failedAlert").style = "display: block;";
        document.getElementById("successAlert").style = "display: none;";
        return;
    }
    var form = new FormData();
    form.append("function", code);

    success = function(result) {
        alert(result)
    }

    sendForm(form, "POST", "/test", success);
}

var validateForm = function() {

    var name = document.getElementById("name").value;
    var description = document.getElementById("description").value;
    var runevery = document.getElementById("runevery").value;
    var scale = document.getElementById("scale").value;
    var code = myCodeMirror.getValue();
    var infinite = document.getElementById("infinite").checked;
    var times = document.getElementById("times").value;
    var schema = document.getElementById("schema").checked;
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    if (scale == "sec") {
        runevery *= 1000;
    } else if (scale == "min") {
        runevery *= 1000 * 60;
    } else if (scale == "hr") {
        runevery *= 1000 * 60 * 60;
    } else if (scale == "days") {
        runevery *= 1000 * 60 * 60 * 24;
    }

    if (name != "" && runevery != "" && scale != "" && username != "" && password != "" && code != "" && (infinite || times != "")) {
        var form = new FormData();
        form.append("name", name);
        form.append("function", code);
        form.append("next", 0);
        form.append("every", runevery);
        form.append("times", infinite ? -1 : times);
        form.append("schema", schema);

        if (description != "") {
            form.append("description", description)
        }

        success = function(result) {
            document.getElementById("successName").innerHTML = form.get("name");
            document.getElementById("successId").innerHTML = result;
            document.getElementById("name").value = "";
            document.getElementById("description").value = "";
            document.getElementById("runevery").value = "";
            document.getElementById("scale").value = "ms";
            document.getElementById("infinite").checked = true;
            document.getElementById("times").value = "";
            document.getElementById("times").disabled = true;
            document.getElementById("schema").checked = false;
            document.getElementById("failedAlert").style = "display: none;";
            document.getElementById("successAlert").style = "display: block;";
        }

        sendForm(form, "PUT", "/schedule", success);

    } else {
        document.getElementById("failedMessage").innerHTML = "You must complete all required fields before you can submit.";
        document.getElementById("failedAlert").style = "display: block;";
        document.getElementById("successAlert").style = "display: none;";
    }
    return false;
}


var sendForm = function(form, verb, path, success) {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": endpoint + path,
        "method": verb,
        "headers": {},
        "beforeSend": function (xhr){
            xhr.setRequestHeader("Authorization", "Basic " + btoa( document.getElementById("username").value + ":" + document.getElementById("password").value ));
        },
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form,
        "success": success,
        "error": function(request, status, errorThrown) {
            document.getElementById("failedMessage").innerHTML = errorThrown;
            document.getElementById("failedAlert").style = "display: block;";
            document.getElementById("successAlert").style = "display: none;";
        }
    }
    $.ajax(settings).done();
}
