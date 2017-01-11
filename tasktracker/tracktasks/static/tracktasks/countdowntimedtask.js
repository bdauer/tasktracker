
/*
This function sets up all of the timer buttons
to find their respective counters when clicked.
*/
function prepareTimerListeners() {

  var startbuttons = document.querySelectorAll('button[id^="start"]');
  var stopbuttons = document.querySelectorAll('button[id^="stop"]');

  addMultipleListeners(startbuttons);
  addMultipleListeners(stopbuttons);
}


/*
Adding listeners on iteration modified from:
http://stackoverflow.com/a/8909792
*/
function addMultipleListeners(buttons) {
    for (var i = 0, len = buttons.length; i < len; i++) {
      var button = buttons[i];
      var newid = button.id.replace(/^\D+/g, '');

      (function(newid) {

        button.addEventListener('click', function(evt) {

            evt.preventDefault();

            if (button.name.includes("start")) {
                startCounter(newid);

            }
            else if (button.name.includes("stop")) {

                stopCounter(newid);
            }
            postAjaxRequest(this, newid);
            changeButton(this, newid);
        });
      })(newid);
    }
  }


/*
Takes a remaining time value
in H{d}M{d}S{d} format
where d is any non-numeric value,
and H and M are optional,
and returns the total seconds.
*/
function toSeconds(time) {
  timeArray = toTimeArray(time);
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
      var counterid = counter.id.replace(/^\D+/g, '');
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
    var buttons = document.querySelectAll('button[id^="start"]');
    for (var i = 0, len = startbuttons.length; i < len; i++) {
        var button = buttons[i];
        var buttonid = button.id.replace(/^\D+/g, '');

        if (buttonid === newid) {
            return {
                button: button,
                buttonid: buttonid
            }
        }
    }
};


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
Start counting down.
*/
function startCounter(newid) {

      var counterobj = findCounter(newid);
      var display = counterobj.counter;
      counterid = counterobj.counterid;
      seconds = counterobj.seconds;


      timer = new CountDownTimer(seconds),
      timeObj = CountDownTimer.parse(seconds);

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
  }

function stopCounter(newid) {
    timer.stop();
    var counterobj = findCounter(newid);
    var display = counterobj.counter;
    counterid = counterobj.counterid;
    seconds = counterobj.seconds;

    timeObj = CountDownTimer.parse(seconds);

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
    console.log(name);
    $.ajax({

        url: '/tracktasks/marktaskcomplete/',
        type: 'POST',
        data: {
                'selected_task': newid,
                // 'start_timer': '',
                'name': name
        }

    })
};


$( prepareTimerListeners );
