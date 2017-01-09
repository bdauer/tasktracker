import CountDownTimer from "countdowntimer";


var startID = /start[\d]+/;

var counterID = /time[\d]+/;

countdown = function() {
    var remainingtime = document.querySelectorAll('span[id^="time"]');
    var startbuttons = document.querySelectorAll('button[id^="start"]');
    var stopbuttons = document.querySelectorAll('button[id^="stop"]');
    return counterID;
}




document.getElementById(startID).onclick = countdown ();


/*
This function sets up all of the timer buttons
to find their respective counters when clicked.
Adding event listeners on iteration informed by:
http://stackoverflow.com/a/8909792
*/
function prepareTimerListeners() {
  var startbuttons = document.querySelectorAll('button[id^="start"]');

  for (var i = 0, len = startbuttons.length; i < len; i++) {
    var newid = startbuttons[i].id.replace(/^\D+/g, '');
    (function(newid) {
      startbuttons[i].addEventListener('click', function() {
        findCounter(newid);
      });
    })(newid);
  }
}

function toSeconds(time) {
  timeArray = toTimeArray(time);
  console.log(timeArray);
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

function toTimeArray(time) {
	time += "";
	return time.split(/\D+/);
}

function findCounter(newid) {
  var counters = document.querySelectorAll('span[id^="time"]');
  for (var i = 0, len = counters.length; i < len; i++) {
    var counter = counters[i];
    var counterid = counter.id.replace(/^\D+/g, '');
    if (counterid === newid) {
      seconds = toSeconds(counter.innerHTML);
      var display = counter,
        timer = new CountDownTimer(seconds),
        timeObj = CountDownTimer.parse(seconds);

      function formatTime(hours, minutes, seconds) {
      console.log(hours + " " + minutes + " " + seconds);
      // need to test for undefined here
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
  }
};

window.onLoad = prepareTimerListeners();
// add event listeners to each element
// when clicked, they should do something

// when task.id start is clicked,
//      strip out the number
//      and modify the timespan ending with that number
//      begin the countdown for task.id time

//      when task.id stop is clicked,
//      stop the countdown for task.id time
