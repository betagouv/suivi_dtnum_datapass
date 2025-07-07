
$(document).ready(function() {
    function getProgress() {
        $.ajax({
            url: "/progress",
            type: "GET",
            dataType: "json",
            success: function(data) {
                $("#progress-bar").css("width", data.progress + "%");
                if(data.progress == 100){
                    $("#progress-label").text("Traitement terminé (" + data.progress + "%)");
                }else if(data.progress == 0){
                    $("#progress-label").text("Pas de traitement (" + data.progress + "%)");
                }else{
                    $("#progress-label").text(data.message +" ... (" + data.progress + "%)");
                }
            },
            error: function(xhr, status, error) {
                console.error("Erreur lors de la récupération de l'état d'avancement : " + error);
            }
        });
     }
     setInterval(getProgress, 20);
});
            

// =============================================================


const importBtn = document.getElementsByClassName("input-file");
const customBtn = document.getElementsByClassName("btn");
const customTxt = document.getElementsByClassName("custom-txt");
const launchBtn = document.querySelector("#start-process");
const errorPopup = document.querySelector("#error_popup");
const resetBtn = document.querySelector("#reset-button");



// launchBtn.addEventListener("click", function(){
//     launchBtn.disabled = true;
//     launchBtn.style.cursor = 'not-allowed';
// });

launchBtn.addEventListener("click", function(){
    if(customTxt[0].innerHTML == "Importer le fichier de suivi" || customTxt[1].innerHTML == "Importer le fichier d'export"){
        errorPopup.classList.add("show");
    }else{
        launchBtn.disabled = true;
        launchBtn.style.cursor = 'not-allowed';
        resetBtn.disabled = true;
        resetBtn.style.cursor = 'not-allowed';
        resetBtn.href = "#";
        errorPopup.classList.remove("show");

    };
});

for (let i = 0; i < customBtn.length; i++) {
    customBtn[i].addEventListener("click", function() {
      importBtn[i].click();
    });
  };

  for (let i = 0; i < customTxt.length; i++) {
    customTxt[i].addEventListener("click", function() {
      importBtn[i].click();
    });
  };

  for (let i = 0; i < importBtn.length; i++) {
    importBtn[i].addEventListener("change", function() {
      if (importBtn[i].files.length > 0) {
        const fileName = importBtn[i].files[0].name;
        customTxt[i].innerHTML = fileName;
      } else {
        customTxt[i].innerHTML = "Pas de fichier...";
      }
    });
  };




// function check(){
//     if(customTxt[0] == "Importer le fichier de suivi" || customTxt[1] == "Importer le fichier d'export"){
//         return false;
//         console.log("false, pas importé");
//     }else{
//         return true;
//         console.log("true, importé");
//     };
// };

// const exportInput = document.querySelector(".output-file");
// const exportTxt = document.querySelector(".export-txt");
// const exportBtn = document.querySelector(".btn-export");

// document.getElementById("reset-button").onclick = function() {
//     document.getElementById("reset").submit()
// };
