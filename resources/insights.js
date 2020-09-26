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
    valueNames: ['name', 'failureRate']
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
