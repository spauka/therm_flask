// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

angular.module('app.controllers', [])
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
