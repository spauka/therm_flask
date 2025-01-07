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
    .directive('highchart', ["$http", function ($http) {
        function link(scope, element, attrs, outerDir) {
            // Get shortcuts to useful values
            var historic = scope.historic;
            var sensors = scope.sensors;
            var fridge = scope.fridge;
            var sensor_name = attrs.therm;
            var thermid = attrs.thermid;

            // Load settings
            var count = detectmob() ? pointCountMobile : pointCountDesktop;
            var customStyle = (thermid in customSensorStyles) ? customSensorStyles[thermid] : {};
            var thermChartStyle = $.extend(true, structuredClone(defaultChartStyle), customStyle);
            var dataURL = new URL(thermid, scope.baseURL);
            dataURL.searchParams.append("count", count);

            // Fill in data for the template
            scope.sensor = sensor_name;
            scope.col_name = thermid;
            scope.table_color = thermChartStyle.table.color;

            var createChart = function (chartStyle, overwriteRanges=true) {
                // Merge chart styles with default
                chartStyle = $.extend(true, chartStyle, thermChartStyle);
                if (overwriteRanges) {
                    // Calculate ranges for historic and nonhistoric graphs
                    var ranges = historic ? historicRanges : normalRanges;
                    chartStyle.rangeSelector.buttons = ranges;
                    chartStyle.rangeSelector.selected = (historic ? 6 : 1);
                }
                console.debug(chartStyle);
                var chart = $('#' + thermid).highcharts('StockChart', chartStyle);

                // Add the chart to the list of charts
                scope.charts[thermid] = chart;
            };

            // Get the data for the chart and then create the chart
            $http({ method: 'GET', url: dataURL.href, cache: false, responseType: 'json' })
                .then(function (response) {
                    var data = response.data;

                    // Construct the series
                    var series = {
                        series: [{
                            name: sensor_name,
                            data: data,
                            type: "area",
                            units: "K"
                    }]
                };
                    createChart(series);
                });

            element.on('$destroy', function () {
            });
        }
        return {
            link: link,
            restrict: 'E',
            transclude: true,
            templateUrl: 'includes/highcharts.html',
        };
    }]);
