window.onload = function(){
    var actualBtn = document.getElementById('inputFile');

    var fileChosen = document.getElementById('file-chosen');

    actualBtn.addEventListener('change', function(){
    fileChosen.textContent = this.files[0].name
    })
}