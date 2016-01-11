'use strict';
(function() {
    var app = angular.module('solarCalc', ['config']);
    
    var restAPI = config.restAPI;
    var coordRegExp = /(\-?)(\d{1,2})\:(\d{1,2})\:(\d{1,2}\.\d)/;
    var coordFormat = '$1$2°$3′$4″';
    var iso8601RegExp = /(\d{4})-(\d{2})-(\d{2})T(\d{2})\:(\d{2})\:(\d{2})([+-])(\d{2})\:(\d{2})/;
    var dateFormat =  '$3.$2.$1 $4:$5:$6 (UTC$7$8:$9)';
    var dateFormatShort = '$4:$5:$5';
    var degreeRegExp = /(\-?\d{1,2})\:(\d{1,2})\:(\d{1,2}\.\d)/;
    var hourAngleRegExp = /(\-?\d{1,2})\:(\d{1,2})\:(\d{1,2}\.\d)/;
    var hourRegExp = /(\-?\d{1,2})\:(\d{1,2})\:(\d{1,2})/;
  
    app.filter('coordLat', function() {
      return function(input) {
        if (input === undefined) return;
        input = input.replace(coordRegExp, coordFormat);
        if (input[0] !== '-') {
          return input + ' N';
        }
        else {
          return input.substr(1) + ' S'; 
        }
      };
    });

    app.filter('coordLon', function() {
      return function(input) {
        if (input === undefined) return;
        input = input.replace(coordRegExp, coordFormat);
        if (input[0] !== '-') {
          return input + ' E';
        }
        else {
          return input.substr(1) + ' W';
        }
      };
    });
   
    app.filter('round', function() {
      return function(input) {
        return Math.round(Number(input));
      };
    });

    app.filter('isodate', function() {
      return function(input, format) {
        if (input === undefined) return;
        if (format === 'short') {
          input = input.replace(iso8601RegExp, dateFormatShort);
        }
        else {
          input = input.replace(iso8601RegExp, dateFormat);
        }
        return input;
      };
    });

    app.filter('degree', function() {
      return function(input) {
        if (input === undefined) return;
        var match = degreeRegExp.exec(input);
        var degrees = Number(match[1]);
        var minutes = Number(match[2]);
        var seconds = Number(match[3]);
        var total_degrees = degrees + minutes/60.0 + seconds/3600.0;
        return '' + Math.round(100.0*total_degrees)/100.0 + '°';
      };
    });

    app.filter('hourangle', function() {
      return function(input) {
        if (input === undefined) return;
        var match = hourAngleRegExp.exec(input);        
        var degrees = Number(match[1]);
        var minutes = Number(match[2]);
        var seconds = Number(match[3]);
        var total_degrees = degrees + minutes/60.0 + seconds/3600.0;
        return '' + degrees + ' hrs, ' + minutes + ' min,  ' + seconds + ' sec';
      };
    });
    
    app.filter('hours', function() {
      return function(input, format) {
        if (input === undefined) return;
        var match = hourRegExp.exec(input);        
        var degrees = Number(match[1]);
        var minutes = Number(match[2]);
        var seconds = Number(match[3]);
        var total_degrees = degrees + minutes/60.0 + seconds/3600.0;
        if (format === 'short') {
          return '' + degrees + ':' + ('00'+minutes).slice(-2) + ':' + ('00'+seconds).slice(-2);
        }
        else {
          return '' + degrees + ' hrs, ' + minutes + ' min,  ' + seconds + ' sec';
        }
      };
    });

    app.controller('CalcController', ['$http', function($http) {
      this.location_info = null;
      this.stats = null;
      var ctrl = this;

      this.fetchCity = function(city) {
        this.location_info = 'fetching...';

        $http.get(restAPI + '/location?city=' + city).then(function(data) {
          ctrl.location_info = data.data;
          // We have basic location information, so let us fetch also stats
          $http.get(restAPI + '/stats?city=' + city).then(function(data) {
            ctrl.stats = data.data;
          }, function(err) {
            ctrl.stats = null;
          });
        }, function(err) {
          ctrl.location_info = null;
        });
      };
    }]);

    app.controller('LocationFormController', ['$http', function($http) {
      var ctrl = this;
      this.city = null; 
      this.cities = {'cities': [
        {'name': 'Helsinki',
          'lat': '24.9382401',
          'lon': '60.1698125',
          'elev': '7.153307'},
        {'name': 'Budapest',
          'lat': '47.4984056',
          'lon': '19.0407578',
          'elev': '106.463295'}
        ]};
        
      $http.get(restAPI + '/cities').then(function(data) {
        ctrl.cities = data.data;
      }, function(err) {
        console.log('Failed to read in city data from REST API: ' + err);
      });
    }]);

})();
