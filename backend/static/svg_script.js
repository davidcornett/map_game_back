
//to-do: click to deselect county

var selectedCounties = [];


function incrCountyNum() {
    //increase counter in html by 1
    document.getElementById('countyCount').innerText ++;
}

function decrCountyNum() {
    //decrease counter in html by 1
    document.getElementById('countyCount').innerText --;
}

function setCounties() {
    //console.log(document.getElementById('map').contentDocument);
    var area = 0;
    var map = document.getElementById('map').contentDocument;
    var updatedStyle = "fill:green;stroke:#ffffff;stroke-opacity:1;fill-opacity:1;stroke-width:0.25;stroke-miterlimit:4;stroke-dasharray:none";
    var defaultStyle = "font-size:12px;fill:#d0d0d0;fill-rule:nonzero;stroke:#000000;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel";
    var states = map.getElementsByTagName('path');
    var currentCounty = null;

    for (i=0; i<states.length - 1; i++) {
        // Loops through each county; does not loop through last <path>, which is for state borders
        // select or deselect a county upon click, depending on whether it was already selected
        states[i].addEventListener('click', async function(e) {
            
            let target = e.currentTarget;  // needed to work with later promise
            let id = target.getAttribute('id');
            
            // DESELECT if already selected - subtract area, clear formatting, remove from array, and decrement counter
            if (selectedCounties.includes(id)) {
                area -= await getArea(id);
                target.setAttribute('style', defaultStyle);
                selectedCounties = selectedCounties.filter(function(f) {return f !== id })
                decrCountyNum()

            // SELECT if not selected yet - add area, apply special formatting, add to array, and increment counter
            } else {
                area += await getArea(id);
                target.setAttribute('style', updatedStyle);
                selectedCounties.push(id); 
                incrCountyNum();
            } 
            document.getElementById('area').innerText = area;


        })        

        // when user hovers over a county, 'Current County' display shows the county name
        states[i].addEventListener('mouseover', function(f) {
            currentCounty = f.currentTarget.getAttribute('inkscape:label');
            let countyHolder = document.getElementById('currentCounty');
            countyHolder.innerText = currentCounty;
        })
    }      
}

function getCounties() {
    let counties = document.getElementById('counties');
    counties.value = selectedCounties;
}

async function getArea(id){
    //return  100;
    let url = 'http://127.0.0.1:6205/get_area/';
    let test = [];
    await fetch(url.concat(id)).then(
        async (value) => {
            //console.log(1);
            //console.log(value);
            return await value.json()
        }
    ).then(
        (value) => {
            test = value;
        }
    )
    //console.log(test);
    return test;
    //console.log(selectedCounties);
    


}

window.addEventListener('load', setCounties);
document.querySelector('#submit_country').addEventListener('click', getCounties);
document.getElementById('countyCount')
