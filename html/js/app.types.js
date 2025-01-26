// The fridges to sparkline
class FridgeSparkLine {
    fridge_name;
    fridge_db_name;
    fridge_js_name;
    txt_color;
    color;
    multiplier;
    constructor(fridge_name, fridge_db_name, fridge_js_name, txt_color, color, multiplier) {
        this.fridge_name = fridge_name;
        this.fridge_db_name = fridge_db_name;
        this.fridge_js_name = fridge_js_name;
        this.txt_color = txt_color;
        this.color = color;
        this.multiplier = multiplier;
    }

    fridge_data_uri() {
        var constructed_url = new URL(this.fridge_db_name, data_uri);
        constructed_url.searchParams.set("summary", "");
        return constructed_url.toString();
    }
}

// Date ranges in HighStock
// Note: Can be extended with additional options from
// https://api.highcharts.com/highstock/rangeSelector.buttons
class HighStockRangeSelector {
    type;
    count;
    text;
    title;
    constructor(type, count, text, title) {
        this.type = type;
        this.count = count;
        this.text = text;
        if (title === undefined)
            this.title = text;
        else
            this.title = title;
    }
}