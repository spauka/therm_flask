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
    var name = seriesOptions.name;
    var units = seriesOptions.units;
    var number = "";
    if (this.y < 0.01)
        number = this.y.toExponential(3) + units;
    else
        number = this.y.toFixed(3) + units;
    var dt = new Date(this.x);
    var datetime = tooltipDateFormatter.format(dt);
    var tooltip = `
        <span style="font-size: xx-small">${datetime}</span><br />
        <span style="color: ${this.color}">●</span> ${name}: <b>${number}</b>
    `;
    return tooltip;
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
    var historic = scope.historic;

    var xMin = chart.xAxis[0].min;
    var xMax = chart.xAxis[0].max;

    if (e.rangeChanged === false) {
        return;
    }

    // Set up historic chart updater
    if (historic && (xMax - xMin) <= (5 * 86400000) + 1000) {
        var url = new URL(scope.col_name, scope.baseURL);
        url.searchParams.append("start", xMin);
        url.searchParams.append("stop", xMax);
        chart.showLoading('Loading Data...');
        var request = new Request(url, {destination: "json", cache: "no-store"});
        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                chart.series[0].setData(data);
                chart.hideLoading();
                chart.series[0].zoomed = true;
            });
    } else if (historic && chart.series[0].zoomed === true) {
        // Restore original data
        console.debug("Resetting data");
        chart.series[0].setData(chart.options.navigator.series.data);
        chart.series[0].zoomed = false;
    }

    // Don't update ranges on a linkedUpdate - true if we are resizing or adding data to all charts.
    if (chart.linkedUpdate) {
        return;
    }
    var charts = scope.charts;
    $.each(charts, function (i, setChart) {
        setChart = setChart.highcharts();
        if (setChart.container == chart.container) {
            return;
        }
        setChart.linkedUpdate = true;
        setChart.xAxis[0].setExtremes(xMin, xMax, true, false);
        setChart.linkedUpdate = false;
    });
}