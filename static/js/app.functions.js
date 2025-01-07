// (c) 2025 Sebsatian Pauka
// This code is licensed under MIT license (see LICENSE file for details)

function resolveCssColor(className, property="color") {
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