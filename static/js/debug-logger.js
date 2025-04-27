(function() {
  // Check if Django debug mode is false
  if (window.DJANGO_DEBUG === false) {
    // Store original console methods
    var originalConsole = {};
    for (var method in console) {
      if (typeof console[method] === 'function') {
        originalConsole[method] = console[method];
      }
    }

    // Replace console methods with empty functions
    var methodsToSilence = ['log', 'debug', 'info', 'warn', 'error', 'assert', 'dir', 'dirxml', 'trace', 'group', 'groupEnd', 'time', 'timeEnd', 'count', 'table'];

    methodsToSilence.forEach(function(method) {
      if (console[method]) {
        console[method] = function() {};
      }
    });

    // Optional: Provide a way to temporarily enable logging if needed (e.g., for a specific session)
    // window.enableConsoleLogging = function() {
    //   for (var method in originalConsole) {
    //     console[method] = originalConsole[method];
    //   }
    //   console.log("Console logging enabled.");
    // };
  }
})();