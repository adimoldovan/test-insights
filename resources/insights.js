showLoader()

// region clipboard
let clipboardCells = document.getElementsByClassName("clipboard");

Array.from(clipboardCells).forEach(function (item) {
    item.addEventListener("click", function () {
        let textAreaEl = document.createElement('textarea');
        textAreaEl.value = this.innerText;
        textAreaEl.setAttribute('readonly', '');
        textAreaEl.style.position = 'absolute';
        textAreaEl.style.left = '-9999px';
        document.body.appendChild(textAreaEl);
        textAreaEl.select();
        document.execCommand('copy');
        document.body.removeChild(textAreaEl);
    });
});

// endregion

// region define list options
let options = {
    valueNames: ['name', 'failureRate', 'results']
};

let specList = new List('specs', options);

// endregion

// region filters
// Filter out cases with 0 failure rate
let filterNoFailuresChkBx = document.getElementById("filterNoFailures")
filterNoFailuresChkBx.addEventListener('change', function () {
    filterByFailuresRate()
});

// endregion

// region default options
specList.sort('failureRate', {order: "desc"});
filterByFailuresRate()
// endregion

// specs container padding
setSpecsContainerPadding()

hideLoader()

/*
* Filters listed test cases based in failure rate and the state of the control checkbox
* Checkbox checked => filter out test cases with 0 failure rate
* */
function filterByFailuresRate() {
    specList.filter(function (item) {
        let failureRate = parseInt(item.values()["failureRate"]);
        if (filterNoFailuresChkBx.checked) {
            return failureRate > 0;
        } else {
            return failureRate >= 0;
        }
    });
}

function setSpecsContainerPadding() {
    let headerHeight = document.getElementById("main-header").offsetHeight;
    console.log(headerHeight)

    let stickyTableCells = document.getElementsByClassName("tbl-header");

    Array.from(stickyTableCells).forEach(function (cell) {
        cell.style.top = "" + headerHeight
    });
}

function showLoader() {
    let loader = document.getElementById("loader")
    loader.style.display = 'block';
}

function hideLoader() {
    let loader = document.getElementById("loader")
    loader.style.display = 'none';
}
