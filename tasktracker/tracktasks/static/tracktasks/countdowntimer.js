

// modified from
// http://stackoverflow.com/a/20618517



function CountDownTimer(duration, granularity) {
  this.duration = duration;
  this.granularity = granularity || 1000;;
  this.tickFtns = [];
  this.running = false;
}

CountDownTimer.prototype.start = function() {
  if (this.running) {
    return;
  }
  this.running = true;
  var start = Date.now(),
    that = this,
    diff, obj;

  (function timer() {
    diff = that.duration - (((Date.now() - start) / 1000) | 0);

    if (diff > 0) {
      setTimeout(timer, that.granularity);
    } else {
      diff = 0;
      that.running = false;
    }

    obj = CountDownTimer.parse(diff);
    that.tickFtns.forEach(function(ftn) {
      ftn.call(this, obj.hours, obj.minutes, obj.seconds);
    }, that);
  }());
};

CountDownTimer.prototype.stop = function() {
    this.running = false;
    this.tickFtns = [];
}

CountDownTimer.prototype.onTick = function(ftn) {
  if (typeof ftn === 'function') {
    this.tickFtns.push(ftn);
  }
  return this;
};

CountDownTimer.prototype.expired = function() {
  return !this.running;
};

CountDownTimer.parse = function(seconds) {
  var date = new Date(null);
  date.setSeconds(seconds);
  date = date.toISOString().substr(11, 8);
  timeArray = toTimeArray(date);
  if (timeArray[0] == "00" && timeArray[1] == "00") {
    return {
      'seconds': timeArray[2]
    }
  } else if (timeArray[0] === "00") {
    return {
      'minutes': timeArray[1],
      'seconds': timeArray[2]
    }
  } else {
    return {
      'hours': timeArray[0],
      'minutes': timeArray[1],
      'seconds': timeArray[2]
    }
  }
};
