/*         ______________________________________
  ________|                                      |_______
  \       |           SmartAdmin WebApp          |      /
   \      |      Copyright © 2014 MyOrange       |     /
   /      |______________________________________|     \
  /__________)                                (_________\

 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 * =======================================================================
 * SmartAdmin is FULLY owned and LICENSED by MYORANGE INC.
 * This script may NOT be RESOLD or REDISTRUBUTED under any
 * circumstances, and is only to be used with this purchased
 * copy of SmartAdmin Template.
 * =======================================================================
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 * =======================================================================
 * original filename: app.config.js
 * filesize: ??
 * author: Sunny (@bootstraphunt)
 * email: info@myorange.ca
 * =======================================================================
 *
 * APP CONFIGURATION (HTML/AJAX/PHP Versions ONLY)
 * Description: Enable / disable certain theme features here
 * GLOBAL: Your left nav in your app will no longer fire ajax calls, set
 * it to false for HTML version
 */
	$.navAsAjax = true;
/*
 * Impacts the responce rate of some of the responsive elements (lower
 * value affects CPU but improves speed)
 */
	var throttle_delay = 350,
/*
 * The rate at which the menu expands revealing child elements on click
 */
	menu_speed = 235,
/*
 * Turn on JarvisWidget functionality
 * dependency: js/jarviswidget/jarvis.widget.min.js
 */
	enableJarvisWidgets = true,
/*
 * Warning: Enabling mobile widgets could potentially crash your webApp
 * if you have too many widgets running at once
 * (must have enableJarvisWidgets = true)
 */
	enableMobileWidgets = false,
/*
 * These elements are ignored during DOM object deletion for ajax version
 * It will delete all objects during page load with these exceptions:
 */
	ignore_key_elms = ["#header, #left-panel, #main, div.page-footer, #shortcut, #divSmallBoxes, #divMiniIcons, #divbigBoxes, #voiceModal, script"];

/*
 * Define data uri
 */
$.data_uri = "https://qsyd.sydney.edu.au/therm/data/";

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
