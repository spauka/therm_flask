angular.module('app.controllers', [])
  .factory('settings', ['$rootScope', function($rootScope){
    // supported languages

    var settings = {
        therm_colors: {
            "Fifty_K_Pt": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axis": 0
            },
            "Four_K_Pt": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axis": 0
            },
            "Four_K_RuO": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axis": 0
            },
            "Still_RuO": {
                "foreground": "jarviswidget-color-orange",
                "background": "txt-color-orange",
                "axis": 1
            },
            "Fifty_mK_RuO": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axis": 2
            },
            "MC_Speer": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axis": 2
            },
            "CMN": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axis": 2
            },
            "MC_CMN": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axis": 2
            },
            "MC_Pt": {
                "foreground": "jarviswidget-color-purple",
                "background": "txt-color-purple",
                "axis": 3
            },
            "MC_RuO": {
                "foreground": "jarviswidget-color-pink",
                "background": "txt-color-pink",
                "axis": 0
            },
            "Fifty_K": {
                "foreground": "jarviswidget-color-purple",
                "background": "txt-color-purple",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Four_K": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Still": {
                "foreground": "jarviswidget-color-yellow",
                "background": "txt-color-yellow",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "MC": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Probe": {
                "foreground": "jarviswidget-color-teal",
                "background": "txt-color-teal",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Magnet": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axis": 0,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Four_K_Pt_Front": {
                "foreground": "jarviswidget-color-pink",
                "background": "txt-color-pink",
                "axis": 3,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Fifty_K_Pt_Front": {
                "foreground": "jarviswidget-color-magenta",
                "background": "txt-color-magenta",
                "axis": 3,
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "P4": {
                "foreground": "jarviswidget-color-pink",
                "background": "txt-color-pink",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "P5": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "Flow": {
                "foreground": "jarviswidget-color-orange",
                "background": "txt-color-orange",
                "axisLabel": "Flow",
                "tickLabel": "A.U.",
            },
            "Dump4": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "Dump3": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "PProbe": {
                "foreground": "jarviswidget-color-blueLight",
                "background": "txt-color-blue",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "PIVC": {
                "foreground": "jarviswidget-color-redLight",
                "background": "txt-color-red",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "POVC": {
                "foreground": "jarviswidget-color-greenLight",
                "background": "txt-color-green",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "STILL": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "IVC": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "OVC": {
                "foreground": "jarviswidget-color-pink",
                "background": "txt-color-pink",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "PStill": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "Condensing": {
                "foreground": "jarviswidget-color-pink",
                "background": "txt-color-pink",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "Backing": {
                "foreground": "jarviswidget-color-yellow",
                "background": "txt-color-yellow",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "Tank": {
                "foreground": "jarviswidget-color-green",
                "background": "txt-color-green",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "AirBacking": {
                "foreground": "jarviswidget-color-blueLight",
                "background": "txt-color-blue",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
                "axisType": "logarithmic",
            },
            "VC": {
                "foreground": "jarviswidget-color-purple",
                "background": "txt-color-purple",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "PROBE": {
                "foreground": "jarviswidget-color-orange",
                "background": "txt-color-purple",
                "axisType": "logarithmic",
                "axisLabel": "Pressure (mbar)",
                "tickLabel": "mbar",
            },
            "DryPumpCurrent": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axisLabel": "Current (amps)",
                "tickLabel": "Amps",
                "min": 0,
                "max": 5,
            },
            "BoosterPumpCurrent": {
                "foreground": "jarviswidget-color-teal",
                "background": "txt-color-teal",
                "axisLabel": "Current (amps)",
                "tickLabel": "Amps",
                "min": 0,
                "max": 5,
            },
            "DryPumpSpeed": {
                "foreground": "jarviswidget-color-orange",
                "background": "txt-color-orange",
                "axisLabel": "Speed (Hz)",
                "tickLabel": "Hz",
                "min": 0,
                "max": 120,
            },
            "BoosterSpeed": {
                "foreground": "jarviswidget-color-orangeDark",
                "background": "txt-color-orangeDark",
                "axisLabel": "Speed (Hz)",
                "tickLabel": "Hz",
                "min": 0,
                "max": 100,
            },
            "DryPumpTemp": {
                "foreground": "jarviswidget-color-purple",
                "background": "txt-color-purple",
                "axisLabel": "Temperature (°C)",
                "tickLabel": "°C",
                "min": 0,
                "max": 165,
                "plotBands": [{ // Warning
                    "from": 150,
                    "to": 160,
                    "color": 'rgba(255, 0, 0, 0.1)',
                    "label": {
                        "text": "Warning",
                    }}, { // Error
                    "from": 160,
                    "to": 200,
                    "color": 'rgba(255, 0, 0, 0.3)',
                    "label": {
                        "text": "Error",
                    }},
                ],
            },
            "DryPumpCoolingBlockTemp": {
                "foreground": "jarviswidget-color-magenta",
                "background": "txt-color-magenta",
                "axisLabel": "Temperature (°C)",
                "tickLabel": "°C",
                "min": 0,
                "max": 75,
                "plotBands": [{ // Warning
                    "from": 60,
                    "to": 70,
                    "color": 'rgba(255, 0, 0, 0.1)',
                    "label": {
                        "text": "Warning",
                    }}, { // Error
                    "from": 70,
                    "to": 80,
                    "color": 'rgba(255, 0, 0, 0.3)',
                    "label": {
                        "text": "Error",
                    }},
                ],
            },
            "BoosterPumpTemp": {
                "foreground": "jarviswidget-color-redLight",
                "background": "txt-color-redLight",
                "axisLabel": "Temperature (°C)",
                "tickLabel": "°C",
                "min": 0,
                "max": 175,
                "plotBands": [{ // Warning
                    "from": 160,
                    "to": 170,
                    "color": 'rgba(255, 0, 0, 0.1)',
                    "label": {
                        "text": "Warning",
                    }}, { // Error
                    "from": 170,
                    "to": 200,
                    "color": 'rgba(255, 0, 0, 0.3)',
                    "label": {
                        "text": "Error",
                    }},
                ],
            },
            "BoosterCoolingBlockTemp": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axisLabel": "Temperature (°C)",
                "tickLabel": "°C",
                "min": 0,
                "max": 75,
                "plotBands": [{ // Warning
                    "from": 60,
                    "to": 70,
                    "color": 'rgba(255, 0, 0, 0.1)',
                    "label": {
                        "text": "Warning",
                    }}, { // Error
                    "from": 70,
                    "to": 80,
                    "color": 'rgba(255, 0, 0, 0.3)',
                    "label": {
                        "text": "Error",
                    }},
                ],
            },
            "ProbeTemp": {
                "foreground": "jarviswidget-color-blue",
                "background": "txt-color-blue",
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Setpoint": {
                "foreground": "jarviswidget-color-orangeDark",
                "background": "txt-color-orangeDark",
                "axisLabel": "Temperature (K)",
                "tickLabel": "K",
            },
            "Heater": {
                "foreground": "jarviswidget-color-red",
                "background": "txt-color-red",
                "axisLabel": "Output Percentage (%)",
                "tickLabel": "%",
                "min": 0,
                "max": 100,
            },
        },
    };

    return settings;

  }])

  .controller('FridgeViewController', ['$scope', '$routeParams', function($scope, $routeParams) {
    if ('fridge' in $routeParams) {
      $scope.pagetitle = $routeParams.fridge.replace('_', ' ');
    } else {
      $scope.pagetitle = 'Dashboard';
    }
    $scope.params = $routeParams;
  }])

  .controller('TempTableController', ['$scope', '$http', '$interval', 'settings', function($scope, $http, $interval, settings) {
    var fridge = $scope.$parent.params.fridge;
    if ('supp' in $scope.$parent.params) {
      var supp = $scope.$parent.params.supp;
      var URL = "https://qphys1114.research.ext.sydney.edu.au/therm_flask/"+fridge+"/"+supp+"/?current";
      var sen_URL = "https://qphys1114.research.ext.sydney.edu.au/therm_flask/"+fridge+"/"+supp+"/?sensors";
      //var URL = "http://physics.usyd.edu.au/~spauka/therm_flask/"+fridge+"/"+supp+"/?current";
      //var sen_URL = "http://physics.usyd.edu.au/~spauka/therm_flask/"+fridge+"/"+supp+"/?sensors";
    } else {
      var URL = "https://qphys1114.research.ext.sydney.edu.au/therm_flask/"+fridge+"/data/?current";
      var sen_URL = "https://qphys1114.research.ext.sydney.edu.au/therm_flask/"+fridge+"/data/?sensors";
    }
    var charts = $scope.charts = {};
    $http({method: 'GET', url: sen_URL, cache: false, responseType: 'json'})
      .success(function (data, status) {
          for (var i = 0; i < data.length; i++) {
            if (data[i].column_name in settings.therm_colors) {
              data[i].color = settings.therm_colors[data[i].column_name];
            }
          }
          $scope.sensors = data;
          $scope.$parent.sensors = data;
      });
    this.addChart = function(thermid, chart, series) {
      charts[thermid] = {chart: chart, series: series};
    };
    this.getCharts = function() {
      return charts;
    };
    $scope.fetch = function() {
      $scope.code = null;
      $scope.response = null;

      $http({method: 'GET', url: URL, cache: false, responseType: 'json'})
        .success(function (data, status) {
          var Time = new Date(data.Time);
          if ($scope.$parent.Time == Time.toString())
            return;
          $scope.$parent.Time = Time.toString();

          for (var item in data) {
              $scope[item] = data[item];
          }
          for (therm in data) {
            if (therm in charts) {
                charts[therm].chart.series[charts[therm].series].addPoint([Time.getTime(), data[therm]], true, true);
            }
          }
        })
        .error(function (data, status) {
          $scope.Four_K_RuO = "Request Failed";
        });

    };
    interval = $interval(function() {$scope.fetch();}, 5000);
    $scope.$on('$destroy', function() {
      // Make sure that the interval is destroyed too
      $interval.cancel(interval);
    });
    $scope.fetch();
  }])
  .controller('HistoricViewController', ['$scope', '$http', '$interval', 'settings', function($scope, $http, $interval, settings) {
    var fridge = $scope.$parent.params.fridge;
    var supp = $scope.$parent.params.supp;
    console.log(supp);
    if (typeof supp == 'undefined')
      supp = "data";
    var sen_URL = "https://qphys1114.research.ext.sydney.edu.au/therm_flask/"+fridge+"/"+supp+"/?sensors";
    var charts = $scope.charts = {};
    $http({method: 'GET', url: sen_URL, cache: false, responseType: 'json'})
      .success(function (data, status) {
          for (var i = 0; i < data.length; i++) {
            if (data[i].column_name in settings.therm_colors) {
              data[i].color = settings.therm_colors[data[i].column_name];
            }
          }
          $scope.sensors = data;
          $scope.$parent.sensors = data;
      });
    this.addChart = function(thermid, chart, series) {
      charts[thermid] = {chart: chart, series: series};
    };
    this.getCharts = function() {
      return charts;
    }
  }])
  .controller('SmartAppController', ['$scope', '$route', '$routeParams', '$location', function($scope, $route, $routeParams, $location) {
    $scope.$route = $route;
    $scope.$location = $location;
    $scope.$routeParams = $routeParams;
    $scope.range = function(num) {
        if (isNaN(num) || num <= 0)
            return new Array();
        return new Array(Math.ceil(num));
    }
  }])
  .directive('thermtable', [function() {
    return {
      restrict: 'E',
      scope: {color: '@'},
      templateUrl: 'includes/thermtable.html',
      transclude: true,
      controller: 'TempTableController',
    };
  }])
  .directive('histcharts', [function() {
    return {
      restrict: 'E',
      scope: {},
      templateUrl: 'includes/histchart.html',
      transclude: true,
      controller: 'HistoricViewController'
    };
  }])
  .directive('highchart', [function() {
    function link(scope, element, attrs, thermtable) {
      if (typeof thermtable[0] !== 'undefined') {
        thermtable = thermtable[0];
        var historic = false;
      }
      else {
        thermtable = thermtable[1];
        var historic = true;
      }
      if (scope.therm != -1)
        var therms = [scope.$parent.sensors[parseInt(scope.therm)]];
      else 
        var therms = scope.$parent.sensors;
      fridge = scope.$parent.params.fridge;
      if ('supp' in scope.$parent.params)
        var data = scope.$parent.params.supp;
      else
        var data = 'data';
      count = 20000;
      if (detectmob())
        count = 100;
      var seriesOptions = [];
      var seriesCounter = 0;
      var thermid = scope.thermid;

      var createChart = function() {
        cdate = new Date();
        Highcharts.setOptions({
            global: {
                timezoneOffset: cdate.getTimezoneOffset()
            }
        });
        if (scope.therm == -1) {
          $('#'+thermid).css('height', '800px');
          var yAxis = [
            {title: {
                  text: 'Temperature (mK)'
              },
              startOnTick: true,
              endOnTick: true,
              minRange: 3000,
              floor: 0,
              min: 0
            }, {title: {
                  text: 'Temperature (mK)'
              },
              startOnTick: true,
              endOnTick: true,
              minRange: 1000,
              floor: 0,
              min: 0
            },
            {title: {
              text: 'Temperature (mK)'
            },
            startOnTick: true,
            endOnTick: true,
            minRange: 100,
            floor: 0,
            min: 0
            },
            {title: {
              text: 'Temperature (mK)'
            },
            startOnTick: true,
            endOnTick: true,
            minRange: 10000,
            floor: 0
            },
          ];
          if (detectmob()) {
            yAxis.forEach(function(axis) {axis.labels = {enabled: false}; axis.title.text = null;});
          }
        } else {
          var yAxis = {
              title: {
                  text: seriesOptions[0].axisLabel,
              },
              startOnTick: true,
              endOnTick: true,
              type: seriesOptions[0].axisType,
              min: seriesOptions[0].min,
              max: seriesOptions[0].max,
              plotBands: seriesOptions[0].plotBands,
          };
        }

        // Calculate ranges for historic and nonhistoric graphs
        var ranges = [];
        if (!historic){
          ranges = ranges.concat([{
                type: 'minute',
                count: 10,
                text: '10m'
            }, {
                type: 'hour',
                count: 1,
                text: '1h'
            }, {
                type: 'hour',
                count: 2,
                text: '2h'
            }, {
                type: 'hour',
                count: 5,
                text: '5h'
            }]);
        }
        ranges = ranges.concat([{
            type: 'day',
            count: 1,
            text: '1d'
        }, {
            type: 'day',
            count: 3,
            text: '3d'
        }]);
        if (historic) {
          ranges = ranges.concat([{
                type: 'day',
                count: 7,
                text: '7d'
            }, {
                type: 'month',
                count: 1,
                text: '1m'
            }, {
                type: 'month',
                count: 2,
                text: '2m'
            }, {
                type: 'month',
                count: 3,
                text: '3m'
            }]);
        }
        ranges = ranges.concat([{
            type: 'all',
            text: 'All'
        }]);

        $('#'+thermid).highcharts('StockChart', {
            chart: {
                zoomType: 'x'
            },
            rangeSelector: {
                inputEnabled: $('#'+thermid).width() > 480,
                buttons: ranges,
                selected: (historic ? 6 : 1),
            },
            navigator: {
              adaptToUpdatedData: (historic ? false : true),
            },
            scrollbar: {
              liveRedraw: (historic ? false : true),
            },
            xAxis: {
                ordinal: false,
                events: {
                  setExtremes: function(e) {
                    chart = $('#'+thermid).highcharts();
                    if (e.min == chart.xAxis[0].min && e.max == chart.xAxis[0].max) 
                      return;
                  },
                  afterSetExtremes: function() {
                    var chart = $('#'+thermid).highcharts();

                    var xMin = chart.xAxis[0].min;
                    var xMax = chart.xAxis[0].max;

                    // Set up historic chart updater
                    if (historic && (xMax-xMin) <= (5*86400000)+1000) {
                      var url = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/'+fridge+'/'+data+'/'+thermid+'?start='+xMin+'&stop='+xMax;
                      chart.showLoading('Loading Data...');
                      $.getJSON(url, function (data) {
                        chart.series[0].setData(data);
                        chart.hideLoading();
                      });
                    } else if (historic) {
                      chart.series[0].setData(seriesOptions[0].data);
                    }

                    if(chart.zooming)
                      return;
                    charts = thermtable.getCharts();
                    $.each(charts, function(i, setChart) {
                      if (setChart.chart.container == chart.container){
                        return;
                      }
                      setChart.chart.zooming = true;
                      setChart.chart.xAxis[0].setExtremes(xMin, xMax, true);
                      setChart.chart.zooming = false;
                    });
                  },
                }
            },
            yAxis: yAxis,
            plotOptions: {
              series: {
                connectNulls: false
              },
              area: {
                threshold: null
              }
            },
            series: seriesOptions,
            tooltip: seriesOptions[0].tooltip,
            zooming: false,
            historic: historic,
        });
        if (scope.therm != -1)
          thermtable.addChart(thermid, $('#'+thermid).highcharts(), 0);
        else {
          seriesOptions.forEach(function (therm) {thermtable.addChart(therm.column_name, $('#'+thermid).highcharts(), therm.column_id)});
        }
      };

      $.each(therms, function(i, therm) {
        if (!historic) {
          var url = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/'+fridge+'/'+data+'/'+therm.column_name+'?count='+count;
        } else {
          var url = 'https://qphys1114.research.ext.sydney.edu.au/therm_flask/'+fridge+'/'+data+'/'+therm.column_name+'?hourly';
        }
        $.getJSON(url, function (data) {
          if (scope.therm != -1) {
            $('#'+therm.column_name+'-name').text(therm.name);
            $('#'+therm.column_name).addClass(therm.color.background);
            $('#'+therm.column_name).parents().eq(2).addClass(therm.color.foreground);
            // Create the chart
            var lineColor = $('.'+therm.color.background).css('color') || Highcharts.getOptions().colors[0];
            var fillColor = Highcharts.Color(lineColor).setOpacity(0.25).get('rgba');
            var type = 'area';
            var axis = 0;
            if ('axisType' in therm.color)
              var axisType = therm.color.axisType;
            else
              var axisType = 'linear';
            if ('axisLabel' in therm.color)
              var axisLabel = therm.color.axisLabel;
            else
              var axisLabel = 'Temperature (mK)';
            if ('tickLabel' in therm.color)
              var tickLabel = therm.color.tickLabel;
            else
              var tickLabel = 'mK';
            if ('min' in therm.color)
                var min = therm.color.min;
            else
                var min = null;
            if ('max' in therm.color)
                var max = therm.color.max;
            else
                var max = null;
            if ('plotBands' in therm.color)
                var plotBands = therm.color.plotBands;
            else
                var plotBands = null;

            var formatter = function() {
              var number = "";
              if (this.y < 0.01)
                number = this.y.toExponential(3) + tickLabel;
              else
                number = this.y.toFixed(3) + tickLabel;
              var dt = new Date(this.x);
              var dts = $.format.date(dt, "E, dd MMM, HH:mm:ss");
              return "<span style=\"font-size: xx-small\">"+dts + "</span><br/>" + therm.name + ": <b>" + number + "</b>";
            };
          } else {
            $('#combined-name').text("Combined View");
            $('#combined').parents().eq(2).addClass("jarviswidget-color-blueDark");
            var lineColor = $('.'+therm.color.background).css('color') || Highcharts.getOptions().colors[0];
            var type = 'line';
            var axis = therm.color.axis;
            var axisType = 'linear';
            var formatter = null;
          }
          var id = seriesOptions.push({
              name: therm.name,
              data: data,
              type: type,
              fillColor: fillColor,
              color: lineColor,
              yAxis: axis,
              tooltip: {
                  formatter: formatter,
                  valueSuffix: tickLabel,
                  valueDecimals: 2,
              },
              axisType: axisType,
              axisLabel: axisLabel,
              min: min,
              max: max,
              plotBands: plotBands,
          });
          seriesOptions[id-1].column_id = id-1;
          seriesOptions[id-1].column_name = therm.column_name;
          seriesCounter += 1;
          if ( seriesCounter == therms.length )
            createChart();
    })});

    element.on('$destroy', function() {
        thermid = scope.thermid;
        chart = $("#"+thermid).highcharts();
        if (chart)
            chart.destroy();
        $('#'+thermid).text("");
      });
    }
    return {
        link: link,
        restrict: 'E',
        scope: { therm: '@', thermid:'@' },
        templateUrl: 'includes/highcharts.html',
        require: ['?^thermtable', '?^histcharts'],
        replace: true,
    };
  }]);
;
