
# InterACTWEL Proposal



## Group members
##### Majid Farahani: hosseinm@oregonstate.edu
##### Hoda Tahami: tahamih@oregonstate.edu


## Description of our project
The limited nature of our shared resources drives the need for assistance to effectively coordinate demand,
 allocation, and efficient use of water, energy, and land within communities. This reality, compounded by threatened
 resource quality, requires coordination among stakeholders whose livelihoods depend on food and energy production and
 availability of water for consumptive and non- consumptive uses; these include: farmers, tribes, water managers, dam
 operators, industries, recreationalists, government agencies, and environmentalists. **InterACTWEL**, a secure and
  intelligent computer-aided decision support tool, empowers such actors to collaborate and coordinate management of natural
   resources over time. This highly flexible and navigable tool can be utilized in times of environmental disturbance or
    during implementation of new agricultural or environmental policies. Its intuitive interface examines impacts to goals,
    operations, and livelihoods for smarter natural resource management (i.e. adaptive management). To do so, this tool
     contains advanced scientific models and interactive optimization algorithms that allow individual actors to identify
      potential adaptation strategies while learning how those strategies affect other actors.


## Data:

1. http://www.oregon.gov/owrd/Pages/maps/index.aspx
2. https://www.nrcs.usda.gov/wps/portal/nrcs/main/or/technical/dma/gis/
3. https://water.usgs.gov/maps.html

## Interface Design:
#### project name:
1. **SoilConsWeb:**
The Project aims to develope, test and implement a tool to support the decisions of stakeholders on soil
 and landscapes conservation issues (Spatial-DSS)
http://soilconsweb.ariesgeo.com/index.php?lang=inglese
#
![SoilConsWeb](img/prop2.jpeg)
#
2. **WRESTORE** is a web-based, user-friendly, interactive, transparent, and participatory decision
 support system for helping land owners, government agencies, policy makers, planners, and other stakeholders
  design a distributed system of conservation practices in their watersheds.
http://wrestore.iupui.edu/
#
![WRESTORE](img/prop1.jpeg)
#














![InterACTWEL](img/pic1.jpg)

# Interface Sketch
![Sketch1](img/sketch1.jpg)
![Sketch2](img/sketch2.jpg)
![sketch3](img/sketch3.jpg)

# Design Scheme

## Color palette
First, we add all the requierd css libraries and script files.

```html
 

    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.css"/>
    <link href="https://fonts.googleapis.com/css?family=Titillium+Web" rel="stylesheet">
    <link rel="stylesheet" type="text/css" media="all" href="css/style.css" />
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/chroma-js/1.3.4/chroma.min.js"></script>
    <script type="text/javascript" src="https://cloudybay.github.io/leaflet.latlng-graticule/leaflet.latlng-graticule.js"></script>

    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js"></script>
```


![colorpalette](img/colorpalette.PNG)


```html
    // 6. Set function for color ramp
    colors = chroma.scale('set1').colors(13);
    function setColor(density) {
        var id = 0;
        if (density == 13) { id = 12; }
        else if (density == 12) { id = 11; }
        else if (density == 11) { id = 10; }
        else if (density == 10) { id = 9; }
        else if (density == 9) { id = 8; }
        else if (density == 8) { id = 7; }
        else if (density == 7) { id = 6; }
        else if (density == 6) { id = 5; }
        else if (density == 5) { id = 4; }
        else if (density == 4) { id = 3; }
        else if (density == 3) { id = 2; }
        else if (density == 2) { id = 1; }
        else  { id = 0; }
        return colors[id];
    }
    // 7. Set style function that sets fill color.md property equal to cell tower density
    function style(feature) {
        return {
            fillColor: setColor(feature.properties.Subbasin),
            fillOpacity: 0.4,
            weight: 2,
            opacity: 1,
            color: '#b4b4b4',
            dashArray: '4'
        };
    }
```

## Fonts 

```html
<link href="https://fonts.googleapis.com/css?family=Titillium+Web" rel="stylesheet">
```

```html
body {
    height: 100%;
    padding: 5px;
    margin: 5px;
    font-family: Titillium, sans-serif;
}
```

## Icons
for this project I need 3 different icons for point data
On font awesome icons the below icon is the icon we use for the data centers

```html
return L.marker(latlng, {icon: L.divIcon({className: 'fa fa-database  marker-color-' + (id + 1).toString() })});
```

![Database](img/database.PNG)


For food processors we use glyphicon

```html
return L.marker(latlng, {icon: L.divIcon({className: 'glyphicon glyphicon-grain marker-color-' + (id + 1).toString() })});
```

For enrgy sector we use an icon from font awesome

```html
 return L.marker(latlng, {icon: L.divIcon({className: 'fa fa-bolt marker-color-' + (id + 1).toString() })});
```

![Icon](img/icon.PNG)


## Multimedia

```html
 <script>
                var  myDataPoint = L.marker([45.819842, -118.0]).addTo(mymap);
                myDataPoint.bindPopup('<iframe src="//www.youtube.com/embed/OA2bVMIb9Po" width="560px" height="315px" ></iframe>', {
                    maxWidth : 560});
            </script>
```

![Multimedia](img/video1.PNG)