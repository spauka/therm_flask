// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

function resolveCssColor(className, property = "color") {
    // Resolve CSS color from the class name
    // Check if the color has already been resolved
    if (className in resolveCssColor.cache)
        return resolveCssColor.cache[className];
    // Create a new div with the class in the document
    var body = document.body;
    var div = document.createElement("div");

    // Add the requested style and make it invisible
    div.classList.add(className);
    div.style.display = "None";

    // Add the element to the page and compute the color.
    body.appendChild(div);
    var color = window.getComputedStyle(div).getPropertyValue(property);

    // Cleanup
    body.removeChild(div);

    resolveCssColor.cache[className] = color;
    return color;
}
resolveCssColor.cache = {};

function tooltipFormatter(pointFormat) {
    var seriesOptions = this.series.userOptions;
    var axisOptions = this.series.chart.yAxis[0].userOptions ;
    var name = seriesOptions.name;
    var units = axisOptions.title.unit;
    var number = "";
    if (this.y < 0.01)
        number = this.y.toExponential(3) + " " + units;
    else
        number = this.y.toFixed(3) + " " + units;
    var dt = new Date(this.x);
    var datetime = tooltipDateFormatter.format(dt);
    var tooltip = `
        <span style="font-size: xx-small">${datetime}</span><br />
        <span style="color: ${this.color}">●</span> ${name}: <b>${number}</b>
    `;
    return tooltip;
}

function fetchWithAbort(request, controllers) {
    const abrt = new AbortController();
    controllers.push(abrt);

    // Calculate how long the request takes and log this
    const startTime = performance.now();

    var get = fetch(request, { signal: abrt.signal }).finally(() => {
        // Remove controller when done
        const idx = controllers.indexOf(abrt);
        if (idx > -1) {
            controllers.splice(idx, 1);
        }

        // Log the time for the request to finish
        const requestTime = (performance.now() - startTime).toFixed(2);
        console.debug("Request to", request.url, "took", requestTime, "ms");
    });

    return get;
}

function populateGraphs(sensors, charts, data, historic=false) {
    // Get the number of elements
    const count = data["time"].length;
    const time_arr = Array.from(data["time"], (timestamp) => new Date(timestamp).getTime());
    // Load each sensor
    sensors.forEach(element => {
        const sens_arr = data[element.column_name];
        // Prepare the data for the sensor
        const data_arr = Array.from({ length: count }, (_, i) => [time_arr[i], sens_arr[i]]);
        if (element.column_name in charts) {
            const chart = charts[element.column_name];
            const linkedUpdateState = chart.linkedUpdate;
            chart.linkedUpdate = true;
            chart.series[0].setData(data_arr);
            if (historic) {
                chart.originalData = data_arr;
                chart.navigator.series[0].setData(data_arr);
            }
            chart.hideLoading();
            chart.linkedUpdate = linkedUpdateState;
        } else {
            console.warn("Couldn't find chart for column: " + element.column_name);
        }
    });
}

function setExtremes(e) {
    var chart = e.target.chart;
    e.rangeChanged = true;
    // Check if the range is actually changing
    if (e.min == chart.xAxis[0].min && e.max == chart.xAxis[0].max)
        e.rangeChanged = false;
}

function afterSetExtremes(e) {
    var chart = e.target.chart;
    var scope = chart.userOptions.scope;
    var charts = scope.charts;
    var historic = scope.historic;

    // Don't update ranges on other charts on a linkedUpdate -
    // true if we are resizing or adding data to all charts.
    if (chart.linkedUpdate) {
        return;
    }

    if (e.rangeChanged === false) {
        return;
    }

    var xMin = new Date(chart.xAxis[0].min);
    var xMax = new Date(chart.xAxis[0].max);

    // Set up historic chart updater (plus 1s so that 5d range definitely fires)
    const fiveDays = (5 * 1000 * 60 * 60 * 24) + 1000;
    if (historic && (xMax - xMin) <= fiveDays) {
        // Update all charts to a linked update that are showing loading
        Object.keys(charts).forEach(chartName => {
            const setChart = charts[chartName];
            setChart.linkedUpdate = true;
            setChart.xAxis[0].setExtremes(xMin.getTime(), xMax.getTime(), true, false);
            setChart.showLoading('Loading Data...');
        });

        // Make a request for data in the right range
        var url = new URL(scope.baseURL);
        url.searchParams.append("start", xMin.toISOString());
        url.searchParams.append("stop", xMax.toISOString());
        var request = new Request(url, {destination: "json"});
        fetchWithAbort(request, scope.requests)
            .then((response) => response.json())
            .then((data) => {
                // Update all charts to a linked update that are showing loading
                populateGraphs(scope.sensors, charts, data, false);
                Object.keys(charts).forEach(chartName => {
                    const setChart = charts[chartName];
                    setChart.hideLoading();
                    setChart.linkedUpdate = false;
                    setChart.series[0].zoomed = true;
                });
            });
    } else if (historic && chart.series[0].zoomed === true) {
        // Update all charts to a linked update that are showing loading
        Object.keys(charts).forEach(chartName => {
            const setChart = charts[chartName];
            setChart.linkedUpdate = true;
            setChart.xAxis[0].setExtremes(xMin.getTime(), xMax.getTime(), true, false);
            setChart.showLoading('Loading Data...');
        });

        // Update all charts to a linked update that are showing loading
        Object.keys(charts).forEach(chartName => {
            const setChart = charts[chartName];
            setChart.series[0].setData(chart.originalData);
            setChart.hideLoading();
            setChart.linkedUpdate = false;
            setChart.series[0].zoomed = false;
        });
    } else {
        // Otherwise in a normal chart view, just update each other chart to the right range
        Object.keys(charts).forEach(chartName => {
            const setChart = charts[chartName];
            if (setChart.container === chart.container) {
                return;
            }
            setChart.linkedUpdate = true;
            setChart.xAxis[0].setExtremes(xMin.getTime(), xMax.getTime(), true, false);
            setChart.linkedUpdate = false;
        });
    }
}