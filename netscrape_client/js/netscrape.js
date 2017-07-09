var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("code"), {
    "theme": "icecoder"
});


var validateForm = function() {

    var name = document.getElementById("name").value;
    var description = document.getElementById("description").value;
    var runevery = document.getElementById("runevery").value;
    var scale = document.getElementById("scale").value;
    var code = document.getElementById("code").value;
    var infinite = document.getElementById("infinite").checked;
    var times = document.getElementById("times").value;
    var save = document.getElementById("save").checked;
    var schema = document.getElementById("schema").checked;

    if (scale == "sec") {
        runevery *= 1000;
    } else if (scale == "min") {
        runevery *= 1000 * 60;
    } else if (scale == "hr") {
        runevery *= 1000 * 60 * 60;
    } else if (scale == "days") {
        runevery *= 1000 * 60 * 60 * 24;
    }

    if (name != "" && runevery != "" && scale != "" && code != "" && (infinite || times)) {
        var form = new FormData();
        form.append("name", name);
        form.append("function", code);
        form.append("next", 0);
        form.append("every", runevery);
        form.append("times", infinite ? -1 : times);
        form.append("save", save);
        form.append("schema", schema);
        sendForm(form);
    } else {
        document.getElementById("failedMessage").innerHTML = "You must complete all required fields before you can submit.";
        document.getElementById("failedAlert").style = "display: block;";
        document.getElementById("successAlert").style = "display: none;";
    }
    return false;
}


var sendForm = function(form) {
    var settings = {
        "async": true,
        "crossDomain": true,
        "url": endpoint + "/schedule",
        "method": "PUT",
        "headers": {},
        "beforeSend": function (xhr){
            xhr.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));
        },
        "processData": false,
        "contentType": false,
        "mimeType": "multipart/form-data",
        "data": form,
        "success": function(result) {
            document.getElementById("successName").innerHTML = form.get("name");
            document.getElementById("successId").innerHTML = result;
            document.getElementById("name").value = "";
            document.getElementById("description").value = "";
            document.getElementById("runevery").value = "";
            document.getElementById("scale").value = "ms";
            document.getElementById("infinite").checked = true;
            document.getElementById("times").value = "";
            document.getElementById("times").disabled = true;
            document.getElementById("save").checked = true;
            document.getElementById("schema").checked = false;
            document.getElementById("failedAlert").style = "display: none;";
            document.getElementById("successAlert").style = "display: block;";
            myCodeMirror.setValue("# Put your navigator code here.");
        },
        "error": function(request, status, errorThrown) {
            document.getElementById("failedMessage").innerHTML = errorThrown;
            document.getElementById("failedAlert").style = "display: block;";
            document.getElementById("successAlert").style = "display: none;";
        }
    }
    $.ajax(settings).done();
}
