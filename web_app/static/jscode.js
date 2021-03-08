window.onload = function(){
    var actualBtn = document.getElementById('inputFile');

    var fileChosen = document.getElementById('file-chosen');

    actualBtn.addEventListener('change', function(){
    fileChosen.textContent = this.files[0].name
    })
}

function _(el) {
  return document.getElementById(el);
}

function uploadFile() {
  // alert(file.name+" | "+file.size+" | "+file.type);
  var formdata = new FormData($('#form-upload')[0]);
  //formdata.append("inputFile", file);
  var ajax = new XMLHttpRequest();
  ajax.upload.addEventListener("progress", progressHandler, false);
  ajax.addEventListener("load", completeHandler, false);
  ajax.addEventListener("error", errorHandler, false);
  ajax.addEventListener("abort", abortHandler, false);
  ajax.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
        console.log("entered");
        document.getElementById("gen").innerHTML = this.responseText;
    }
  };

  ajax.open("POST", "/submit");
  ajax.send(formdata);
  //ajax.success = function(response) { document.write(response) }
}

function progressHandler(event) {
  _("loaded_n_total").innerHTML = "Uploaded " + event.loaded + " bytes of " + event.total;
  var percent = (event.loaded / event.total) * 100;
  _("progressBar").value = Math.round(percent);
  _("status").innerHTML = Math.round(percent) + "% uploaded... please wait";
}

function completeHandler(event) {
  _("status").innerHTML = event.target.responseText;
  _("progressBar").value = 0; //wil clear progress bar after successful upload
}

function errorHandler(event) {
  _("status").innerHTML = "Upload Failed";
}

function abortHandler(event) {
  _("status").innerHTML = "Upload Aborted";
}