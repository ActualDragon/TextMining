document.addEventListener("DOMContentLoaded",
  function (event) {
    var load = document.getElementById("Load");
    var span = document.getElementsByClassName("close")[0];

    var my_func = function(event) {
    load.style.display = "block";
    console.log("Loading")
    //event.preventDefault();
    };

    span.onclick = function() {
        load.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == load) {
        load.style.display = "none";
        }
    }

    document.getElementById('form').addEventListener('submit', my_func);
  }
);




