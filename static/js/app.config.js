// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

/*
 * Define data uri
 */
const data_uri = "https://qsyd.sydney.edu.au/therm/data/";

/*
 * Default number of points to load on live charts
 */
const pointCountDesktop = 20000;
const pointCountMobile = 1000;

/*
 * Tooltip date format - main graphs
 */
const tooltipDateFormat = {
	weekday: "short",
	year: "2-digit",
	month: "short",
	day: "numeric",
	hour: "numeric",
	minute: "numeric",
	second: "numeric",
	timeZoneName: "shortOffset", // DB only stores offset, not original tz
	hourCycle: "h24" // "h12" for 12 hour time
};
const tooltipDateFormatter = new Intl.DateTimeFormat(undefined, tooltipDateFormat);

/*
 * Define default chart format
 */
function tooltipFormatter() {
    var seriesOptions = this.series.userOptions;
    var name = seriesOptions.name;
    var units = seriesOptions.units;
    var number = "";
    if (this.y < 0.01)
        number = this.y.toExponential(3) + units;
    else
        number = this.y.toFixed(3) + units;
    var dt = new Date(this.x);
    var dts = tooltipDateFormatter.format(dt);
    return "<span style=\"font-size: xx-small\">" + dts + "</span><br/>" + name + ": <b>" + number + "</b>";
};
const currentTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
const defaultChartStyle = {
    table: {
        // Default container colour
        color: "jarviswidget-color-blue",
    },
    chart: {
        zoomType: 'x',
        style: {
            fontFamily: "'Open Sans', Arial, Helvetica, sans-serif",
            fontSize: "13px"
        }
    },
    rangeSelector: {
    },
    time: {
        timezone: currentTimezone,
    },
    xAxis: {
        title: {
            text: "Time",
        },
        ordinal: false, // Don't collapse missing points
    },
    yAxis: {
        title: {
            text: "Temperature (K)",
        },
        startOnTick: true,
        endOnTick: true,
        type: "linear",
    },
    tooltip: {
        formatter: tooltipFormatter,
    },
    plotOptions: {
        series: {
            connectNulls: false
        },
        area: {
            threshold: null
        }
    },
};
const customSensorStyles = {};

/*
 * Define sparkline style (top of page)
 */
const defaultSparkStyle = {
	chart: {
		backgroundColor: null,
		borderWidth: 0,
		type: 'area',
		margin: [2, 0, 2, 0],
		width: 90,
		height: 30,
		style: {
			overflow: 'visible'
		},
		// small optimalization, saves 1-2 ms each sparkline
		skipClone: true
	},
	title: {
		text: ''
	},
	credits: {
		enabled: false
	},
	xAxis: {
		labels: {
			enabled: false
		},
		title: {
			text: null
		},
		tickPositions: [],
		lineWidth: 0,
	},
	yAxis: {
		endOnTick: false,
		startOnTick: false,
		labels: {
			enabled: false
		},
		title: {
			text: null
		},
		tickPositions: []
	},
	legend: {
		enabled: false
	},
	tooltip: {
		hideDelay: 0,
		outside: true,
		shared: true,
	},
	plotOptions: {
		series: {
			animation: false,
			lineWidth: 1,
			shadow: false,
			states: {
				hover: {
					lineWidth: 1
				}
			},
			marker: {
				radius: 1,
				states: {
					hover: {
						radius: 2
					}
				}
			},
			fillOpacity: 0.25,
			softThreshold: false,
		},
	}
};

/*
 * Define enabled sparklines
 * TODO: Load from DB
 */
// To add a new fridge, add a new SparkLine configuration below.
const fridge_sparklines = [
	new FridgeSparkLine("Blue Fridge", "Blue_Fridge", "blue-fridge", "txt-color-blue", "#BCCFD7", 1),
	new FridgeSparkLine("Red Fridge", "Red_Fridge", "red-fridge", "txt-color-red", "#DD9AA9", 1),
	new FridgeSparkLine("Green Fridge", "Green_Fridge", "green-fridge", "txt-color-greenDark", "#B6C3B6", 1),
	new FridgeSparkLine("BlueFors LD", "BlueFors_LD", "ld", "txt-color-blueLight", "#7ab6cc", 1000),
	new FridgeSparkLine("BlueFors XLD", "BlueFors_XLD", "xld", "txt-color-blueDarkBright", "#7FB6FF", 1000),
	new FridgeSparkLine("Friesland", "Friesland", "friesland", "txt-color-teal", "#8FE6E4", 1000),
	new FridgeSparkLine("Murphy", "Murphy", "murphy", "txt-color-teal", "#8FE6E4", 1000),
];

/*
 * Define default graph style
 */
const normalRanges = [
	new HighStockRangeSelector("minute", 10, "10m"),
	new HighStockRangeSelector("hour", 1, "1h"),
	new HighStockRangeSelector("hour", 2, "2h"),
	new HighStockRangeSelector("hour", 5, "5h"),
	new HighStockRangeSelector("day", 1, "1d"),
	new HighStockRangeSelector("day", 3, "3d"),
	new HighStockRangeSelector("all", undefined, "All")
];
const historicRanges = [
	new HighStockRangeSelector("day", 1, "1d"),
	new HighStockRangeSelector("day", 3, "3d"),
	new HighStockRangeSelector("day", 7, "7d"),
	new HighStockRangeSelector("month", 1, "1m"),
	new HighStockRangeSelector("month", 3, "3m"),
	new HighStockRangeSelector("year", 1, "1y"),
	new HighStockRangeSelector("all", undefined, "All")
];

/*
 * END APP.CONFIG
 */
