angular.module('app.controllers', [])
    .factory('settings', ['$rootScope', function ($rootScope) {
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
                "MC_Sample": {
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
                "Sample": {
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
                "ExtraProbe": {
                    "foreground": "jarviswidget-color-magenta",
                    "background": "txt-color-magenta",
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
                "Noise_Head": {
                    "foreground": "jarviswidget-color-red",
                    "background": "txt-color-red",
                    "axis": 0
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
                        }
                    }, { // Error
                        "from": 160,
                        "to": 200,
                        "color": 'rgba(255, 0, 0, 0.3)',
                        "label": {
                            "text": "Error",
                        }
                    },
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
                        }
                    }, { // Error
                        "from": 70,
                        "to": 80,
                        "color": 'rgba(255, 0, 0, 0.3)',
                        "label": {
                            "text": "Error",
                        }
                    },
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
                        }
                    }, { // Error
                        "from": 170,
                        "to": 200,
                        "color": 'rgba(255, 0, 0, 0.3)',
                        "label": {
                            "text": "Error",
                        }
                    },
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
                        }
                    }, { // Error
                        "from": 70,
                        "to": 80,
                        "color": 'rgba(255, 0, 0, 0.3)',
                        "label": {
                            "text": "Error",
                        }
                    },
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
                "Corridor": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Temperature (C)",
                    "tickLabel": "°C",
                },
                "High": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
                "Low": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
                "Delta": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
                "Bounce": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
                "WaterIn": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Temperature (C)",
                    "tickLabel": "°C",
                },
                "WaterOut": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Temperature (C)",
                    "tickLabel": "°C",
                },
                "Helium": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Temperature (C)",
                    "tickLabel": "°C",
                },
                "Oil": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Temperature (C)",
                    "tickLabel": "°C",
                },
                "Current": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axisLabel": "Current (A)",
                    "tickLabel": "A",
                },
                "Dewar_Temp": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Temperature (K)",
                    "tickLabel": "K",
                },
                "Dewar_Volume": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Volume (L)",
                    "tickLabel": "L",
                },
                "Dewar_Level": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Level (cm)",
                    "tickLabel": "cm",
                },
                "Dewar_Pressure": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
                "Purity_Sensor": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Purity (nA)",
                    "tickLabel": "nA",
                },
                "LN2_Level": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Level (%)",
                    "tickLabel": "%",
                },
                "Storage_Pressure": {
                    "foreground": "jarviswidget-color-blue",
                    "background": "txt-color-blue",
                    "axis": 0,
                    "axisLabel": "Pressure (PSI)",
                    "tickLabel": "PSI",
                },
            },
        };

        return settings;

    }])
    .controller('SmartAppController', ['$scope', '$route', '$routeParams', '$location', function ($scope, $route, $routeParams, $location) {
        $scope.$route = $route;
        $scope.$location = $location;
        $scope.$routeParams = $routeParams;
        $scope.range = function (num) {
            if (isNaN(num) || num <= 0)
                return new Array();
            return new Array(Math.ceil(num));
        }
        // This should be a property since it's shared globally
        $scope.lastUpdated = 'Never';
    }])
    .controller('FridgeViewController', ['$scope', '$routeParams', '$http', '$interval', function ($scope, $routeParams, $http, $interval) {
        $scope.pagetitle = $routeParams.fridge.replace('_', ' ');
        $scope.params = $routeParams;
        $scope.sensors = [];
        $scope.values = {};
        $scope.charts = {};

        // Figure out the data URL's for the fridge
        $scope.fridge = $routeParams.fridge;
        $scope.historic = 'historic' in $routeParams;
        if ('supp' in $routeParams) {
            $scope.supp = $routeParams.supp;
            $scope.baseURL = new URL($routeParams.fridge+"/"+$scope.supp+"/", data_uri);
        } else {
            $scope.supp = null;
            $scope.baseURL = new URL($routeParams.fridge+"/data/", data_uri);
        }
        $scope.currentURL = new URL("?current", $scope.baseURL);
        $scope.sensorURL = new URL("?sensors", $scope.baseURL);

        // Create a function to update values on a regular interval
        $scope._lastUpdated = "Never";
        $scope.getLastUpdated = function () {
            return $scope._lastUpdated;
        }
        $scope.updateTime = function (time) {
            $scope._lastUpdated = time;
            $scope.$parent.lastUpdated = time;
        };
        function fetch(updateCharts) {
            $http({ method: 'GET', url: $scope.currentURL.href, cache: false, responseType: 'json' })
                .then(function (response) {
                    var data = response.data;
                    var time = new Date(data.Time);
                    var new_update = time.toString();

                    if ($scope.getLastUpdated() == new_update)
                        return;
                    $scope.updateTime(new_update);

                    for (var therm in data) {
                        $scope.values[therm] = data[therm];
                    }
                    if (updateCharts) {
                        var charts = $scope.charts;
                        for (var therm in data) {
                            if (therm in charts) {
                                var chart = charts[therm].highcharts();
                                chart.series[0].addPoint([time.getTime(), data[therm]], true, true);
                            }
                        }
                    }
                }, function (response) {
                    // Do something smarter here on failure
                    return;
                });
        };
        // Create a periodic update if we are not looking at historic data
        if (!$scope.historic) {
            var fetchInterval = $interval(function () {
                fetch(true);
            }, 5000);
            $scope.$on("$destroy", function () {
                // Cancel downloading new data
                $interval.cancel(fetchInterval);
                // Reset last updated
                $scope.$parent.lastUpdated = "Never";
            });
        }

        // Load the sensors for the fridge
        $http({ method: 'GET', url: $scope.sensorURL.href, cache: true, responseType: 'json' })
            .then(function (response) {
                var data = response.data;
                $scope.sensors = data;
                data.forEach(element => {
                    $scope.values[element.column_name] = NaN;
                });
                // Perform an initial fetch of the values. This occurs even for historic datasets
                fetch(false);
            });

    }]);
