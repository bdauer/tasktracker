"use strict";

/*
This function sets up all of the timer buttons
to find their respective counters when clicked.
*/
function prepareTimerListeners() {

    var buttons = document.getElementsByTagName('button')
    addMultipleListeners(buttons);
}

/*
Adding listeners on iteration modified from:
http://stackoverflow.com/a/8909792
*/
function addMultipleListeners(buttons) {
    for (var i = 0, len = buttons.length; i < len; i++) {
      var button = buttons[i];
      var newid = stripNonNumerics(button.id);


      (function(newid) {

        button.addEventListener('click', function(evt) {

            evt.preventDefault();


            if (button.name.includes("start")) {
                console.log("start");

                var counterobj = findCounter(newid);
                startCounter(newid, counterobj);
                listenForZero(newid, counterobj);
            }
            else if (button.name.includes("stop")) {
                console.log("stop");

                // if there is a timer instance running:
                if (window.hasOwnProperty('timer')) {
                    console.log("there is a timer");
                    stopCounter(newid);
                }
            }
            else if (button.name.includes("completed")) {
                console.log(this);
                moveCompletedTask(this);
            }
            postAjaxRequest(this, newid);
            changeButton(this, newid);
        });
      })(newid);
    }
  }


function listenForZero(newid, counterobj) {
    var display = counterobj.counter;

    var observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                  if (mutation.target.innerHTML == "00s") {
                      var button = findButton(newid);
                      moveCompletedTask(button);
                      postAjaxRequest(button, newid);
                      alert("You have completed your current timed task!")
                      observer.disconnect();
              }
            });
    });
        var config = {attributes: true, childList: true, characterData: true};
        observer.observe(display, config);

    };

/*
Move a completed task
,reformatted,
to the completed tasks list.
*/
function moveCompletedTask(node) {

    // if completed_tasks doesn't exist,
    // create it.
    if (!document.getElementById("completed_tasks")) {
        var completedDiv = document.getElementById("completed_div");
        var newh2 = document.createElement("h2");
        var newUL = document.createElement("ul");
        newh2.innerHTML = "completed tasks";
        newUL.id = "completed_tasks";
        completedDiv.appendChild(newh2);
        completedDiv.appendChild(newUL);
    }

    var completedTasks = document.getElementById("completed_tasks");
    var entry = node.parentNode;
    var entryText = entry.firstChild;
    while (entry.hasChildNodes()) {
        entry.removeChild(entry.firstChild);
    }

    // var newEntry = document.createElement("li");
    // newEntry.appendChild(entryText);
    var newEntry = createLI(entryText);
    entry.parentNode.removeChild(entry);
    completedTasks.insertBefore(newEntry, completedTasks.childNodes[0]);
}

/*
Create a new <li>
with the provided text.
*/
function createLI(text) {

    var newEntry = document.createElement("li");
    newEntry.appendChild(text);
    return newEntry;
}

function postAjaxRequest(button, newid) {
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
      }
  });
    var csrftoken = getCookie('csrftoken');
    var name = button.name;
    console.log(name)
    $.ajax({

        url: '/tracktasks/marktaskcomplete/',
        type: 'POST',
        data: {
                'selected_task': newid,
                'name': name
        }

    })
};

/*
Toggle stop and start buttons for timed tasks.
*/
function changeButton(button, newid) {

    if (button.id.includes("start")) {
        button.id = "stop" + newid;
        button.name = "stop_timer";
        button.innerHTML = "Stop activity";
    }
    else if (button.id.includes("stop")) {
        button.id = "start" + newid;
        button.name = "start_timer";
        button.innerHTML = "Start activity";

    }
}

/*
Return the text with all non-numeric
characters removed.
*/
function stripNonNumerics(text) {
    return text.replace(/^\D+/g, '');
}

/*
Takes a remaining time value
in H{d}M{d}S{d} format
where d is any non-numeric value,
and H and M are optional,
and returns the total seconds.
*/
function toSeconds(time) {
  var timeArray = toTimeArray(time);
  // if only minutes and seconds are present:
  if (timeArray.length === 2) {
  var seconds = timeArray[0];
  }
  else if (timeArray.length === 3) {
    var seconds = (timeArray[0] * 60) + parseInt(timeArray[1]);
  }
  // if hours, minutes and seconds are present:
  else if (timeArray.length > 3) {
    var seconds = (((timeArray[0] * 60) +
        parseInt(timeArray[1])) * 60) +
      parseInt(timeArray[2]);
  }
  return seconds;
}

/*
Takes a time value
n H{d}M{d}S{d} format
where d is any non-numeric value,
and H and M are optional.
Returns an array
containing all of those values
plus an empty string.
*/
function toTimeArray(time) {
	time += "";
	return time.split(/\D+/);
}

/*
Find a counter suffixed with the provided ID.
Return a counter object containing:
    the counter,
    the counter id suffix,
    the counter's remaining time converted to seconds.
*/
function findCounter(newid) {
    var counters = document.querySelectorAll('span[id^="time"]');
    for (var i = 0, len = counters.length; i < len; i++) {
      var counter = counters[i];
    //   var counterid = counter.id.replace(/^\D+/g, '');
      var counterid = stripNonNumerics(counter.id);
      var seconds = toSeconds(counter.innerHTML);

      if (counterid === newid) {
          return {
                    counter: counter,
                    counterid: counterid,
                    seconds: seconds
                };
        };
    };
};

function findButton(newid) {
    var buttons = document.querySelectorAll('button[id^="stop"]');
    for (var i = 0, len = buttons.length; i < len; i++) {
        var button = buttons[i];
        var buttonid = stripNonNumerics(button.id);

        if (buttonid === newid) {
            return button;
        }
    }
};

/*
Start counting down.
*/
function startCounter(newid, counterobj) {
    console.log("counter started");
      var display = counterobj.counter;
      var counterid = counterobj.counterid;
      var seconds = counterobj.seconds;
      var timer = new CountDownTimer(seconds);
      var timeObj = CountDownTimer.parse(seconds);

      // nested to allow access to display
      // when iterating over tickFtns
      // in CountDownTimer.start
      // without changing the original API.
      function formatTime(hours, minutes, seconds) {
          if (typeof hours != "undefined") {
            display.textContent = hours + 'h:' + minutes + 'm:' + seconds + "s";
            }
            else if (typeof minutes != "undefined") {
            	display.textContent = minutes + 'm:' + seconds + "s";
            }
            else {
             display.textContent = seconds + "s";
            }
          }

      formatTime(timeObj.hours, timeObj.minutes, timeObj.seconds);
      timer.onTick(formatTime);
      timer.start();
      window.timer = timer;


  }
/*
Stop counting down.
*/
function stopCounter(newid) {
    console.log(timer);
    timer.stop();
    var counterobj = findCounter(newid);
    var display = counterobj.counter;
    var counterid = counterobj.counterid;
    var seconds = counterobj.seconds;

    var timeObj = CountDownTimer.parse(seconds);

    function formatTime(hours, minutes, seconds) {
        if (typeof hours != "undefined") {
          display.textContent = hours + 'h:' + minutes + 'm:' + seconds + "s";
          }
          else if (typeof minutes != "undefined") {
              display.textContent = minutes + 'm:' + seconds + "s";
          }
          else {
           display.textContent = seconds + "s";
          }
        }
    formatTime(timeObj.hours, timeObj.minutes, timeObj.seconds);
}

/*
Returns a cookie value with the provided name.
*/
function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
          var cookie = jQuery.trim(cookies[i]);
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}

/*
Checks whether a method requires CSRF protection.
*/
function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}


$( prepareTimerListeners );
