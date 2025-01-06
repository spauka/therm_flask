smartApp
    .directive('fridgeview', ['$interval', '$http', function ($interval, $http) {
        function link(scope, element, attrs) {
            // Keep track of the charts that are associated with this table

        }

        return {
            link: link,
        };
    }])
    .directive('thermtable', [function () {
        function link(scope, element, attrs) {
            //debugger
        }

        return {
            restrict: 'E',
            transclude: true,
            templateUrl: 'includes/thermtable.html',
            link: link,
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
            var chartStyle = Highcharts.merge(false, customStyle, defaultChartStyle);
            var dataURL = new URL(thermid, scope.baseURL);
            dataURL.searchParams.append("count", count);

            // If the color of the series is given as a CSS color, resolve it here
            if ("cssColor" in chartStyle.plotOptions.series) {
                element.classList.add(chartStyle.plotOptions.series.cssColor);
                var lineColor = element.css('color');
                chartStyle.plotOptions.series.color = lineColor;
                chartStyle.plotOptions.series.fillColor = new Highcharts.Color(lineColor).setOpacity(0.25).get("rgba");
            }

            // Fill in data for the template
            scope.sensor = sensor_name;
            scope.col_name = thermid;
            scope.table_color = chartStyle.table.color;

            var createChart = function (series) {
                // Calculate ranges for historic and nonhistoric graphs
                var ranges = historic ? historicRanges : normalRanges;
                chartStyle.rangeSelector.buttons = ranges;
                chartStyle.rangeSelector.selected = (historic ? 6 : 1);

                // Get custom options for the line if they exist
                chartStyle.series = series;
                var chart = $('#' + thermid).highcharts('StockChart', chartStyle);
                console.debug(chartStyle);
                console.debug(chart);
            };

            // Get the data for the chart and then create the chart
            $http({ method: 'GET', url: dataURL.href, cache: false, responseType: 'json' })
                .then(function (response) {
                    var data = response.data;

                    // Construct the series
                    var series = [{
                        name: sensor_name,
                        data: data,
                        type: "area",
                        units: "K"
                    }];
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
