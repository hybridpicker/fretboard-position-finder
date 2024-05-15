// Customize the "sfbsfnos" select field on page load
window.onload = function() {
    customizeSelectField("sfbsfnos");
    customizeSelectField("sfbsfpos");
    customizeSelectField("sfbsf");
  
    // If the user clicks anywhere outside the select box, close all select boxes
    document.addEventListener("click", closeAllSelect);
  
    var pos_val = document.getElementById('position_select').value;
    var url_string = window.location.href;
    var url = new URL(url_string);
    pos_val = url.searchParams.get("position_select");
    if (pos_val) {
      getTonesFromDataScales(pos_val);
    } else {
      getTonesFromDataScales('0');
    }
  };
  
  /**
   * Customize the select field by creating custom dropdown elements
   */
  function customizeSelectField(className) {
    var x = document.getElementsByClassName(className);
    for (var i = 0; i < x.length; i++) {
      var selElmnt = x[i].getElementsByTagName("select")[0];
      var a = document.createElement("DIV");
      a.setAttribute("class", "sese");
      a.innerHTML = selElmnt.options[selElmnt.selectedIndex].innerHTML;
      x[i].appendChild(a);
  
      var b = document.createElement("DIV");
      b.setAttribute("class", "slit sehi");
      for (var j = 1; j < selElmnt.length; j++) {
        var c = document.createElement("DIV");
        c.innerHTML = selElmnt.options[j].innerHTML;
        c.addEventListener("click", function(e) {
          var y, k, s, h;
          s = this.parentNode.parentNode.getElementsByTagName("select")[0];
          h = this.parentNode.previousSibling;
          for (var i = 0; i < s.length; i++) {
            if (s.options[i].innerHTML == this.innerHTML) {
              s.selectedIndex = i;
              h.innerHTML = this.innerHTML;
              y = this.parentNode.getElementsByClassName("swasd");
              for (k = 0; k < y.length; k++) {
                y[k].removeAttribute("class");
              }
              this.setAttribute("class", "swasd");
              break;
            }
          }
          h.click();
          document.getElementById("fretboard_form").submit();
        });
        b.appendChild(c);
      }
      x[i].appendChild(b);
      a.addEventListener("click", function(e) {
        e.stopPropagation();
        closeAllSelect(this);
        this.nextSibling.classList.toggle("sehi");
        this.classList.toggle("slar-active");
      });
    }
  }
  
  /**
   * Close all select boxes in the document, except the current select box
   */
  function closeAllSelect(elmnt) {
    var x = document.getElementsByClassName("slit");
    var y = document.getElementsByClassName("sese");
    var arrNo = [];
    for (var i = 0; i < y.length; i++) {
      if (elmnt == y[i]) {
        arrNo.push(i);
      } else {
        y[i].classList.remove("slar-active");
      }
    }
    for (var i = 0; i < x.length; i++) {
      if (arrNo.indexOf(i)) {
        x[i].classList.add("sehi");
      }
    }
  }
  