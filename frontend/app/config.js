'use strict';
(function() {
  var config = angular.module('config', []);

  config.factory('config', function() {
    return {
      restAPI = 'http://localhost:5000';
    };
  });

})();
