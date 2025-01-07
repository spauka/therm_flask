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
const currentTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
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
    series: [{
        color: resolveCssColor("txt-color-blue"),
        fillOpacity: 0.25,
    }],
    time: {
        timezone: currentTimezone,
    },
    plotOptions: {
        series: {
            connectNulls: false
        },
        area: {
            threshold: null
        }
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
};
// Functions can't be deepcopied, so we define them separately. We will
// need to merge defaultChartStyle and defaultChartFunctions together
// to get a full set of defaults.
const defaultChartFunctions = {
    tooltip: {
        formatter: tooltipFormatter,
    },
    xAxis: {
        events: {
            setExtremes: setExtremes,
            afterSetExtremes: afterSetExtremes,
        },
    },
};
const customSensorStyles = {
    Fifty_K_Pt: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
        }],
    },
    Four_K_Pt: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
        }],
    },
    Four_K_RuO: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
        }],
    },
    Still_RuO: {
        table: {
            color: "jarviswidget-color-orange",
        },
        series: [{
            color: resolveCssColor("txt-color-orange"),
        }],
    },
    Fifty_mK_RuO: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
        }],
    },
    MC_Speer: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
        }],
    },
    MC_Sample: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
        }],
    },
    CMN: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
        }],
    },
    MC_CMN: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
        }],
    },
    MC_Pt: {
        table: {
            color: "jarviswidget-color-purple",
        },
        series: [{
            color: resolveCssColor("txt-color-purple"),
        }],
    },
    MC_RuO: {
        table: {
            color: "jarviswidget-color-pink",
        },
        series: [{
            color: resolveCssColor("txt-color-pink"),
        }],
    },
    Fifty_K: {
        table: {
            color: "jarviswidget-color-purple",
        },
        series: [{
            color: resolveCssColor("txt-color-purple"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Four_K: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Still: {
        table: {
            color: "jarviswidget-color-yellow",
        },
        series: [{
            color: resolveCssColor("txt-color-yellow"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    MC: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Sample: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Probe: {
        table: {
            color: "jarviswidget-color-teal",
        },
        series: [{
            color: resolveCssColor("txt-color-teal"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Magnet: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    ExtraProbe: {
        table: {
            color: "jarviswidget-color-magenta",
        },
        series: [{
            color: resolveCssColor("txt-color-magenta"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Four_K_Pt_Front: {
        table: {
            color: "jarviswidget-color-pink",
        },
        series: [{
            color: resolveCssColor("txt-color-pink"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Fifty_K_Pt_Front: {
        table: {
            color: "jarviswidget-color-magenta",
        },
        series: [{
            color: resolveCssColor("txt-color-magenta"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Noise_Head: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
        }],
    },
    P4: {
        table: {
            color: "jarviswidget-color-pink",
        },
        series: [{
            color: resolveCssColor("txt-color-pink"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    P5: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    Flow: {
        table: {
            color: "jarviswidget-color-orange",
        },
        series: [{
            color: resolveCssColor("txt-color-orange"),
            axisLabel: "Flow",
            tickLabel: "A.U.",
        }],
    },
    Dump4: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    Dump3: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    PProbe: {
        table: {
            color: "jarviswidget-color-blueLight",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    PIVC: {
        table: {
            color: "jarviswidget-color-redLight",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    POVC: {
        table: {
            color: "jarviswidget-color-greenLight",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    STILL: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    IVC: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    OVC: {
        table: {
            color: "jarviswidget-color-pink",
        },
        series: [{
            color: resolveCssColor("txt-color-pink"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    PStill: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    Condensing: {
        table: {
            color: "jarviswidget-color-pink",
        },
        series: [{
            color: resolveCssColor("txt-color-pink"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    Backing: {
        table: {
            color: "jarviswidget-color-yellow",
        },
        series: [{
            color: resolveCssColor("txt-color-yellow"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    Tank: {
        table: {
            color: "jarviswidget-color-green",
        },
        series: [{
            color: resolveCssColor("txt-color-green"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    AirBacking: {
        table: {
            color: "jarviswidget-color-blueLight",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
            axisType: "logarithmic",
        }],
    },
    VC: {
        table: {
            color: "jarviswidget-color-purple",
        },
        series: [{
            color: resolveCssColor("txt-color-purple"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    PROBE: {
        table: {
            color: "jarviswidget-color-orange",
        },
        series: [{
            color: resolveCssColor("txt-color-purple"),
            axisType: "logarithmic",
            axisLabel: "Pressure (mbar)",
            tickLabel: "mbar",
        }],
    },
    DryPumpCurrent: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Current (amps)",
            tickLabel: "Amps",
            min: 0,
            max: 5,
        }],
    },
    BoosterPumpCurrent: {
        table: {
            color: "jarviswidget-color-teal",
        },
        series: [{
            color: resolveCssColor("txt-color-teal"),
            axisLabel: "Current (amps)",
            tickLabel: "Amps",
            min: 0,
            max: 5,
        }],
    },
    DryPumpSpeed: {
        table: {
            color: "jarviswidget-color-orange",
        },
        series: [{
            color: resolveCssColor("txt-color-orange"),
            axisLabel: "Speed (Hz)",
            tickLabel: "Hz",
            min: 0,
            max: 120,
        }],
    },
    BoosterSpeed: {
        table: {
            color: "jarviswidget-color-orangeDark",
        },
        series: [{
            color: resolveCssColor("txt-color-orangeDark"),
            axisLabel: "Speed (Hz)",
            tickLabel: "Hz",
            min: 0,
            max: 100,
        }],
    },
    DryPumpTemp: {
        table: {
            color: "jarviswidget-color-purple",
        },
        series: [{
            color: resolveCssColor("txt-color-purple"),
            axisLabel: "Temperature (°C)",
            tickLabel: "°C",
            min: 0,
            max: 165,
            plotBands: [{ // Warning
                from: 150,
                to: 160,
                color: 'rgba(255, 0, 0, 0.1)',
                label: {
                    text: "Warning",
                }
            }, { // Error
                from: 160,
                to: 200,
                color: 'rgba(255, 0, 0, 0.3)',
                label: {
                    text: "Error",
                }
            },
            ],
        }],
    },
    DryPumpCoolingBlockTemp: {
        table: {
            color: "jarviswidget-color-magenta",
        },
        series: [{
            color: resolveCssColor("txt-color-magenta"),
            axisLabel: "Temperature (°C)",
            tickLabel: "°C",
            min: 0,
            max: 75,
            plotBands: [{ // Warning
                from: 60,
                to: 70,
                color: 'rgba(255, 0, 0, 0.1)',
                label: {
                    text: "Warning",
                }
            }, { // Error
                from: 70,
                to: 80,
                color: 'rgba(255, 0, 0, 0.3)',
                label: {
                    text: "Error",
                }
            },
            ],
        }],
    },
    BoosterPumpTemp: {
        table: {
            color: "jarviswidget-color-redLight",
        },
        series: [{
            color: resolveCssColor("txt-color-redLight"),
            axisLabel: "Temperature (°C)",
            tickLabel: "°C",
            min: 0,
            max: 175,
            plotBands: [{ // Warning
                from: 160,
                to: 170,
                color: 'rgba(255, 0, 0, 0.1)',
                label: {
                    text: "Warning",
                }
            }, { // Error
                from: 170,
                to: 200,
                color: 'rgba(255, 0, 0, 0.3)',
                label: {
                    text: "Error",
                }
            },
            ],
        }],
    },
    BoosterCoolingBlockTemp: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisLabel: "Temperature (°C)",
            tickLabel: "°C",
            min: 0,
            max: 75,
            plotBands: [{ // Warning
                from: 60,
                to: 70,
                color: 'rgba(255, 0, 0, 0.1)',
                label: {
                    text: "Warning",
                }
            }, { // Error
                from: 70,
                to: 80,
                color: 'rgba(255, 0, 0, 0.3)',
                label: {
                    text: "Error",
                }
            },
            ],
        }],
    },
    ProbeTemp: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Setpoint: {
        table: {
            color: "jarviswidget-color-orangeDark",
        },
        series: [{
            color: resolveCssColor("txt-color-orangeDark"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Heater: {
        table: {
            color: "jarviswidget-color-red",
        },
        series: [{
            color: resolveCssColor("txt-color-red"),
            axisLabel: "Output Percentage (%)",
            tickLabel: "%",
            min: 0,
            max: 100,
        }],
    },
    Corridor: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (C)",
            tickLabel: "°C",
        }],
    },
    High: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
    Low: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
    Delta: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
    Bounce: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
    WaterIn: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (C)",
            tickLabel: "°C",
        }],
    },
    WaterOut: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (C)",
            tickLabel: "°C",
        }],
    },
    Helium: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (C)",
            tickLabel: "°C",
        }],
    },
    Oil: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (C)",
            tickLabel: "°C",
        }],
    },
    Current: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Current (A)",
            tickLabel: "A",
        }],
    },
    Dewar_Temp: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Temperature (K)",
            tickLabel: "K",
        }],
    },
    Dewar_Volume: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Volume (L)",
            tickLabel: "L",
        }],
    },
    Dewar_Level: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Level (cm)",
            tickLabel: "cm",
        }],
    },
    Dewar_Pressure: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
    Purity_Sensor: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Purity (nA)",
            tickLabel: "nA",
        }],
    },
    LN2_Level: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Level (%)",
            tickLabel: "%",
        }],
    },
    Storage_Pressure: {
        table: {
            color: "jarviswidget-color-blue",
        },
        series: [{
            color: resolveCssColor("txt-color-blue"),
            axisLabel: "Pressure (PSI)",
            tickLabel: "PSI",
        }],
    },
};

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
 * END APP.CONFIG
 */
