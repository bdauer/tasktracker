
/*
This function sets up all of the timer buttons
to find their respective counters when clicked.
*/
function prepareTimerListeners() {
  var startbuttons = document.querySelectorAll('button[id^="start"]');
  console.log(startbuttons);
  //  Adding event listeners on iteration informed by:
  //  http://stackoverflow.com/a/8909792
  for (var i = 0, len = startbuttons.length; i < len; i++) {
    var newid = startbuttons[i].id.replace(/^\D+/g, '');
    (function(newid) {
      startbuttons[i].addEventListener('click', function() {
        startCounter(newid);
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


prepareTimerListeners();

// it works, but on refresh I lose the countdown.
// should make an ajax POST request containing start_timer
