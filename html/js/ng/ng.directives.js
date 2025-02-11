// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

smartApp
    .directive('thermtable', [function () {
        return {
            restrict: 'E',
            transclude: true,
            templateUrl: 'includes/thermtable.html',
        };
    }])
    .directive('highchart', ["$timeout", function ($timeout) {
        function link(scope, element, attrs) {
            // Get shortcuts to useful values
            var historic = scope.historic;
            var sensors = scope.sensors;
            var fridge = scope.fridge;
            var sensor_name = attrs.therm;
            var thermid = attrs.thermid;

            // Load settings
            var count = detectmob() ? pointCountMobile : pointCountDesktop;
            var customStyle = (thermid in customSensorStyles) ? customSensorStyles[thermid] : {};
            var thermChartStyle = $.extend(true, structuredClone(defaultChartStyle), defaultChartFunctions);
            thermChartStyle = $.extend(true, thermChartStyle, customStyle);
            var dataURL = new URL(thermid, scope.baseURL);
            if (!historic)
                dataURL.searchParams.append("count", count);
            else
                dataURL.searchParams.append("hourly", "");

            // Fill in data for the template
            scope.sensor = sensor_name;
            scope.col_name = thermid;
            scope.table_color = thermChartStyle.table.color;

            function createChart(chartStyle, overwriteRanges = true) {
                // Merge chart styles with default
                chartStyle = $.extend(true, chartStyle, thermChartStyle);
                if (overwriteRanges) {
                    // Calculate ranges for historic and nonhistoric graphs
                    var ranges = historic ? historicRanges : normalRanges;
                    chartStyle.rangeSelector.buttons = ranges;
                    chartStyle.rangeSelector.selected = (historic ? 6 : 1);
                }
                var chart = $('#' + thermid).highcharts('StockChart', chartStyle).highcharts();

                // Add the chart to the list of charts
                scope.charts[thermid] = chart;
                return chart;
            };

            // Create the charts and set them to "laoding"
            var chartData = {
                scope: scope,
                navigator: {},
                tooltip: {
                    formatter: tooltipFormatter,
                },
                series: [{
                    name: sensor_name,
                    data: [],
                    type: "area",
                }]
            };
            // Set the navigator to a constant set of data
            if (historic) {
                // For historic datasets, disable the navigator updating
                chartData.navigator.adaptToUpdatedData = false;
            }

            // Defer execution until after the template has finished rendering
            $timeout(function() {
                var chart = createChart(chartData);
                chart.showLoading('Loading Data...');

                // Check if the data for the graph is already loaded
                if (scope.initialData !== null) {
                    populateGraph(thermid, chart, scope.initialData, historic);
                    delete scope.initialData[thermid];
                    scope.loadedCharts.push(thermid);
                    // Clear the initial data array if we've loaded all charts
                    if (scope.loadedCharts.length == scope.sensors.length)
                        delete scope.initialData["time"];
                }
            }, 0);

            element.on('$destroy', function () {
                if (thermid in scope.charts && scope.charts[thermid] !== null) {
                    scope.charts[thermid].destroy();
                    delete scope.charts[thermid];
                }
            });
        }
        return {
            link: link,
            restrict: 'E',
            transclude: true,
            templateUrl: 'includes/highcharts.html',
        };
    }]);
