
/*
 * Define data uri
 */
const data_uri = "https://qsyd.sydney.edu.au/therm/data/";

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
 * END APP.CONFIG
 */
