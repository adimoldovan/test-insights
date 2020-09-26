let coll = document.getElementsByClassName("clipboard");
    let i;

    for (i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            ta = document.createElement('textarea');
            ta.value = this.innerText;
            ta.setAttribute('readonly', '');
            ta.style.position = 'absolute';
            ta.style.left = '-9999px';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
        });
    }

let options = {
        valueNames: ['name', 'failureRate']
    };

    let specList = new List('specs', options);

    let filterNoFailuresChkBx = document.getElementById("filterNoFailures")
    filterNoFailuresChkBx.addEventListener('change', function () {
        filterByFailuresRate()
    });

    specList.sort('failureRate', {order: "desc"});
    filterByFailuresRate()

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
