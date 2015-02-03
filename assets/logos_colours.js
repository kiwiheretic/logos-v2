// Taken from https://docs.djangoproject.com/en/dev/ref/csrf/
var csrftoken = getCookie('csrftoken');
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

// ---- end snippet ----

// Based on http://stackoverflow.com/questions/5524045/jquery-non-ajax-post
// Used for dynamically creating a form to submit data to the server 
// in a non-ajax way
function myFormSubmit(action, method, input) {
    'use strict';
    var form;
    form = $('<form />', {
        action: action,
        method: method,
        style: 'display: none;'
    });
    if (typeof input !== 'undefined' && input !== null) {
        $.each(input, function (name, value) {
            $('<input />', {
                type: 'hidden',
                name: name,
                value: value
            }).appendTo(form);
        });
    }
    var csrf_input;
    csrf_input = $('<input />', {
                type: 'hidden',
                name: 'csrfmiddlewaretoken',
                value: csrftoken
            });
    
    form.append(csrf_input);
    form.appendTo('body').submit();
}
// ---- end snippet ----

$( document ).ready(function() {

  function getColourCode(colour_str) {
  
    var re = /mirc-col(\d+)/g;
    var text = re.exec(colour_str);
    if (text) {
      var colour_code = text[1];
      return colour_code;
    } else {
      return null;
    }; 
     
  }; // getColourCode
  
  // Create a colour array (clrArray) which contains all the mIRC
  // colour information and indexed by the mIRC colour integer number.  
  // This is dynamically derived from the cssRules 'mirc-col0' .. 'mirc-col15'
  // to auto discover the assigned rgb colour.  
  var clrArray = new Array();
  var patt = new RegExp("^\.mirc-col(\\d+)");
  for (var sheet_idx in document.styleSheets) {
      var ss = document.styleSheets[sheet_idx];
      var rules = ss.cssRules || ss.rules; 
      for (var idx in rules) {
         sheet = rules[idx];
         if (patt.test(sheet.cssText)) {
             var match = patt.exec(sheet.cssText);
             var mirc_idx = parseInt(match[1]);
             clrArray[mirc_idx] = sheet.style.background;

         };
      }; 
  };
  console.log(clrArray);
  // ---- end clrArray section ----------
  
  
  // setRoomColours:
  //  Set the web widget colours that display the sample verse
  //  and sample search verse from an ajax request to the server
  //  (which in turn gets the preset colour codes from the database).
  function setRoomColours(room) {
      var url = "/bots/colours/get-room-colours/" + network + "/" + room + "/";
      var normal_patt = new RegExp("^normal-([^\\s]+)");
      var search_patt = new RegExp("^search-([^\\s]+)");
      var clr_patt = new RegExp("(\\d+),(\\d+)");
      $(".colour-elmt").css("color","");
      $(".colour-elmt").css("background","");
      $.get(url, function (data){
          /* on success */
          console.log(data);
          obj_list = JSON.parse(data);
          for (var idx in obj_list) {
             obj = obj_list[idx];
             elmt = obj.fields.element;
             clr = obj.fields.mirc_colour;
             var clr_mch = clr_patt.exec(clr);
             var fg = parseInt(clr_mch[1]);
             var bg = parseInt(clr_mch[2]);
             var bg_str = clrArray[bg];
             var fg_str = clrArray[fg];
             if (normal_patt.test(elmt)) {
               var match = normal_patt.exec(elmt);
               var verse_class = match[1];
               var selector = '#verse-example .'+verse_class;
               console.log(selector);
               
               $(selector).css('color', fg_str);
               $(selector).css('background-color', bg_str);

             }
             if (search_patt.test(elmt)) {
               var match = search_patt.exec(elmt);
               var verse_class = match[1];
               if (verse_class == "words") {
                   var selector = '#search-example u'
               } else {
                   var selector = '#search-example .'+verse_class;
                    
               };
//               console.log(selector);
               
               $(selector).css('color', fg_str);
               $(selector).css('background-color', bg_str);

             }             
//             console.log(elmt);
//             console.log(clr);             
             
          };
          
      });
  }; // getRoomColours

  var btn = "#btn-" + currRoom;
  $(btn).addClass("selected-rm-btn");
  $(btn).removeClass("unselected-rm-btn");
  setRoomColours(currRoom);

  $("#room-buttons").find("button").click(function(evt) {
    $("#room-buttons").find("button").removeClass('selected-rm-btn');
    $("#room-buttons").find("button").addClass('unselected-rm-btn');
    $(evt.target).removeClass('unselected-rm-btn');
    $(evt.target).addClass('selected-rm-btn');
    var currRoom = $(evt.target).attr('data-value');
    setRoomColours(currRoom);
  });
  
  // Change the default selected colour in the colour tables
  // (puts a coloured hilighter rectangle around the selected colour.)
  $( ".mirc-colour" ).click(function(evt) {
    tab = $(evt.target).parents('.colour-tab');
    $(tab).find("td").removeClass('colour-selected');
    $(evt.target).addClass('colour-selected');
  });

  $( ".translation,.verse-ref,.verse-text" ).click(function(evt) {
    fg = $("#foreground-table").find('.colour-selected').css('background-color');
    bg = $("#background-table").find('.colour-selected').css('background-color');
    if (typeof bg != 'undefined' && typeof fg != 'undefined') {
       $(evt.target).css('background-color', bg);
       $(evt.target).css('color', fg);
       var class_str;
       class_str = $("#foreground-table").find('.colour-selected').attr('class');
       var clr1 = getColourCode(class_str);
       class_str = $("#background-table").find('.colour-selected').attr('class');
       var clr2 = getColourCode(class_str);
       $(evt.target).data("colour", clr1+","+clr2);
    } else {
       alert('colour not valid');
    }
  });
  
  // If the 'apply' button is clicked...then send all the colour information,
  // from our verse and search example widgets, to the server.  Its done as 
  // a dynamic form so it can be sent as a full browser post (not an ajax post).
  // (Means less custom javascript work for me.)
  $( "#apply" ).click(function() {
      var data_obj = {};
      $("#verse-example").children().each( function (idx, elmt) {
        if ($(elmt).is("span") || $(elmt).is("div")) {
          clr = $(elmt).data("colour");
          if (clr) {
            key = "normal-" + $(elmt).attr('class').replace(/^(\S*)\s(\S*)/, '$2');
            data_obj[key] = clr;
          }
        };
        
      });
      $("#search-example").children().each( function (idx, elmt) {
        if ($(elmt).is("span") || $(elmt).is("div")) {
          clr = $(elmt).data("colour");
          if (clr) {
            key = "search-" + $(elmt).attr('class').replace(/^(\S*)\s(\S*)/, '$2');
            data_obj[key] = clr;
          }
        };
        
      }); 
      // Now the search word
      clr = $("#search-example u").data("colour");
      if (clr) {
         data_obj["search-words"] = clr;
      };
      
      selected_room = $("#room-buttons").find("button.selected-rm-btn").attr("data-value");
      data_obj["network"] = network;
      data_obj["room"] = selected_room;
      s1 = JSON.stringify(data_obj);
      myFormSubmit('/bots/colours/', 'post', data_obj);
      //$.post('/bots/colours/', data_obj); 
  });  
});