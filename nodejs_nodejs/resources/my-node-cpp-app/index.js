const addon = require('./build/Release/addon');

console.log("Addon loaded:", addon);
console.log("Result from addon.hello():", addon.hello());