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
        $scope.historic = false;
        $scope.toggleHistoric = function(value) {
            $scope.historic = value;
            if (value) {
                $location.search("historic", "");
            } else {
                $location.search("historic", null);
            }
        };
    }])
    .controller('FridgeViewController', ['$scope', '$routeParams', '$interval', '$timeout', function ($scope, $routeParams, $interval, $timeout) {
        $scope.pagetitle = $routeParams.fridge.replace('_', ' ');
        $scope.params = $routeParams;
        $scope.sensors = [];
        $scope.sensorsLoaded = false;
        $scope.values = {};
        $scope.charts = {};
        $scope.loadedCharts = [];
        $scope.initialData = null;
        $scope.requests = [];

        // Check route parameters - if historic is there, force historic on
        const shouldBeHistoric = "historic" in $routeParams;
        if (shouldBeHistoric != $scope.historic) {
            $scope.toggleHistoric(shouldBeHistoric);
        }

        // Figure out the data URL's for the fridge
        $scope.fridge = $routeParams.fridge;
        if ('supp' in $routeParams) {
            $scope.supp = $routeParams.supp;
            $scope.baseURL = new URL($routeParams.fridge + "/supp/" + $scope.supp, data_uri);
        } else {
            $scope.supp = null;
            $scope.baseURL = new URL($routeParams.fridge, data_uri);
        }
        $scope.currentURL = new URL("?current", $scope.baseURL);
        $scope.sensorURL = new URL("?sensors", $scope.baseURL);

        // Create parameters to load initial data
        var count = detectmob() ? pointCountMobile : pointCountDesktop;
        $scope.dataURL = new URL($scope.baseURL);
        if (!$scope.historic)
            $scope.dataURL.searchParams.append("count", count);
        else
            $scope.dataURL.searchParams.append("avg_period", "hour");

        // Create a function to update values on a regular interval
        $scope._lastUpdated = "Never";
        $scope.getLastUpdated = function () {
            return $scope._lastUpdated;
        }
        $scope.updateTime = function (time) {
            $scope._lastUpdated = time;
            $scope.$parent.lastUpdated = time;
        };
        function fetchCurrent(updateCharts) {
            var request = new Request($scope.currentURL, { destination: "json", cache: "no-store" });
            fetchWithAbort(request, $scope.requests)
                .then((response) => response.json())
                .then((data) => {
                    var time = new Date(data.time);
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
                                var chart = charts[therm];
                                chart.linkedUpdate = true;
                                chart.series[0].addPoint([time.getTime(), data[therm]], true, true);
                                chart.linkedUpdate = false;
                            }
                        }
                    }

                    // Force update of the table
                    $scope.$apply();
                }).catch((error) => {
                    if (error.name === 'AbortError') {
                        console.log('Request aborted.');
                    } else {
                        console.error('Request failed:', error);
                    }
                });
        };

        // Start a request to load the initial data
        var request = new Request($scope.dataURL, { destination: "json", cache: "no-store" });
        fetchWithAbort(request, $scope.requests)
            .then((response) => response.json())
            .then((data) => {
                // Convert the time field into Date objects
                data["time"].forEach((timestamp) => new Date(timestamp).getTime());

                // Check that sensors has loaded. If it has, then try to load the data into the
                // charts, otherwise save the data.
                if ($scope.sensorsLoaded) {
                    $scope.loadedCharts = Object.keys($scope.charts);
                    const num_charts = $scope.loadedCharts.length;
                    $scope.loadedCharts.forEach((col_name) => {
                        setTimeout(() => {
                            populateGraph(col_name, $scope.charts[col_name], data, $scope.historic);
                            delete data[col_name];
                        });
                    });
                    if (num_charts != $scope.sensors.length) {
                        // Some charts are still loading
                        console.log(
                            "Saving data for future chart loads since",
                            num_charts,
                            "of",
                            $scope.sensors.length,
                            "charts loaded."
                        );
                        $scope.initialData = data;
                    } else {
                        // Delete initial data load, not needed any more
                        $scope.initialData = null;
                    }
                } else {
                    // All charts are still loading
                    $scope.initialData = data;
                }
            }).catch((error) => {
                if (error.name === 'AbortError') {
                    console.log('Request aborted.');
                } else {
                    console.error('Request failed:', error);
                }
            });

        // Load the sensors for the fridge
        var request = new Request($scope.sensorURL, { destination: "json", cache: "no-store" });
        fetchWithAbort(request, $scope.requests)
            .then((response) => response.json())
            .then((data) => {
                $scope.sensors = data;
                data.forEach(element => {
                    $scope.values[element.column_name] = NaN;
                });
                // Trigger an update of the page with the new sensor values
                $scope.$apply();
                $scope.sensorsLoaded = true;

                // Create a periodic update if we are not looking at historic data. This is not worth setting
                // up until the sensors are loaded
                if (!$scope.historic) {
                    var fetchInterval = $interval(function () {
                        fetchCurrent(true);
                    }, 5000);
                    $scope.$on("$destroy", function () {
                        // Cancel downloading new data
                        $interval.cancel(fetchInterval);
                        // Reset last updated
                        $scope.$parent.lastUpdated = "Never";
                    });
                }
                // Perform an initial fetch of the values. This occurs even for historic datasets
                fetchCurrent(true);

                console.log("Loaded",$scope.sensors.length,"sensors for Fridge",$scope.fridge,"("+$scope.supp+")");
            }).catch((error) => {
                if (error.name === 'AbortError') {
                    console.log('Request aborted.');
                } else {
                    console.error('Request failed:', error);
                }
            });

        // Abort all in-progress requests when the scope is destroyed
        $scope.$on('$destroy', function () {
            $scope.requests.forEach(controller => controller.abort()); // Abort all requests
            $scope.requests.length = 0; // Clear the array
            console.log('All in-progress requests cancelled');
        });
    }]);
