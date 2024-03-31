
async function getCountyIDs(){
    
    //let url = 'http://127.0.0.1:6205/get_ids';
    let url = 'http://127.0.0.1:6205/svg';
    let test = [];
    await fetch(url).then(
        async (value) => {
            return await value.json()
        }
    ).then(
        (value) => {
            test = value
        }
    )
    return test;
    //console.log(selectedCounties);
    
}

async function setCounties() {
    //var selectedCounties = [1, 2];
    var selectedCounties = await getCountyIDs();

    var updatedStyle = "fill:green;stroke:#ffffff;stroke-opacity:1;fill-opacity:1;stroke-width:0.25;stroke-miterlimit:4;stroke-dasharray:none";
    //var updatedStyle = "transform-origin: 25% 25%;fill:green;stroke:#ffffff;stroke-opacity:1;fill-opacity:1;stroke-width:0.25;stroke-miterlimit:4;stroke-dasharray:none";

    for (var key of Object.keys(selectedCounties)) {
        console.log(key);
        let map = document.getElementById('map').contentDocument;
        let path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        //console.log(selectedCounties[key]['d']);
        path.setAttribute("id", key);
        path.setAttribute("d", selectedCounties[key]['d']);

        
        map.documentElement.appendChild(path);
        let myPathBox = path.getBBox();
        console.log(myPathBox);
        path.setAttribute("style", updatedStyle);
    }

}

window.addEventListener('load', setCounties);
