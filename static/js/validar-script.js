document.addEventListener("DOMContentLoaded",
  function (event) {
    Hide_Form = function(id){
        document.getElementById(id).style.display = 'none';
    }

    SetVariable = function(edad,id){
        document.getElementById(id).value = edad;
        console.log(edad)
    }

    Hide_Element = function(id) {
        document.getElementById(id).setAttribute(hidden, "hidden")
    }

  }
);




