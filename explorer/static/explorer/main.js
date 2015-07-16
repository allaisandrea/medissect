//////////////////////////////////////////////////////////
// Initialization ////////////////////////////////////////    
//////////////////////////////////////////////////////////

var ne_lat = 0.0, ne_lng = 0.0, sw_lat = 0.0, sw_lng = 0.0;
var bounds_changed_timeout = null;
var selected_provider = {"npi": 0};
var selected_procedure_index = -1;
var procedure_list;
var procedure_search_string = "";
var provider_search_string = "";
var providers_on_table = {};

var procedure_request_timeout_timer;
var procedure_request_counter = 0;
var provider_request_timeout_timer;
var provider_request_counter = 0;
var map_data_request_timeout_timer;
var map_data_request_counter = 0;

var map;
var infowindow;
var infowindow_selector = document.createElement('select');
infowindow_selector.setAttribute(
  "onchange", 
  "on_infowindow_selector_change(this)");
var infowindow_providers;
var provider_search_marker = new google.maps.Marker();

google.maps.event.addDomListener(window, 'load', initialize);

request_procedure_list();

function initialize() {
  var mapCanvas = document.getElementById('map-canvas');
  var mapOptions = {
    center: new google.maps.LatLng(42.37, -71.12),
    zoom: 15,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(mapCanvas, mapOptions);
  infowindow = new google.maps.InfoWindow();
  
  google.maps.event.addListener(map, 'bounds_changed', on_bounds_changed);
  google.maps.event.addListener(map, 'click', on_map_click);
  map.data.addListener('mouseover', on_marker_mouseover);
//   map.data.addListener('mouseout', on_marker_mouseout);
  map.data.addListener('click', on_marker_click);
  map.data.setStyle(set_feature_style);
  
}

//////////////////////////////////////////////////////////
// Requests //////////////////////////////////////////////    
//////////////////////////////////////////////////////////

function request_map_data(){
  var status_box = document.getElementById("status_box");
  status_box.innerHTML = "Waiting for data..."
  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else {  // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  
  map_data_request_timeout_timer = setTimeout(function() {
    map_data_request_counter += 1;
    if(map_data_request_counter < 2)
      request_map_data();
    else
      map_data_request_counter = 0;
  }, 3000);
    
  xmlhttp.onreadystatechange=function() {on_server_response(xmlhttp);};
  xmlhttp.open(
    "GET", 
    "map_data?ne_lat=" + String(ne_lat) + 
    "&ne_lng=" + String(ne_lng) +
    "&sw_lat=" + String(sw_lat) +
    "&sw_lng=" + String(sw_lng) +
    "&proc_code=" + 
      (selected_procedure_index >= 0 ? 
        procedure_list[selected_procedure_index][0]: 
        "all"),
    true);
  xmlhttp.send();
}

function request_procedure_list(){
  var table = document.getElementById('procedure_table');
  if(table){
    while(table.rows.length > 1){
      table.deleteRow(1);
    }
    var row = table.insertRow(1);
    var cell = row.insertCell(0);
    cell.innerHTML = "Waiting for data..."
  }
  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else {  // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  
  
  procedure_request_timeout_timer = setTimeout(function() {
    procedure_request_counter += 1;
    if(procedure_request_counter < 2)
      request_procedure_list();
    else
      procedure_request_counter = 0;
  }, 3000);
  
  xmlhttp.onreadystatechange=function() {on_server_response(xmlhttp);};
  xmlhttp.open(
    "GET", 
    "procedure_list?npi=" + String(selected_provider["npi"]) +
    "&str=" + procedure_search_string,
    true);
  xmlhttp.send();
}

function request_provider_list(){
  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else {  // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
  
  provider_request_timeout_timer = setTimeout(function() {
    provider_request_counter += 1;
    if(provider_request_counter < 2)
      request_provider_list();
    else
      provider_request_counter = 0;
  }, 3000);
      
  xmlhttp.onreadystatechange=function() {on_server_response(xmlhttp);};
  xmlhttp.open(
    "GET", 
    "provider_list?str=" + provider_search_string,
    true);
  xmlhttp.send();
}

function request_location(str){
  if (window.XMLHttpRequest) {
    // code for IE7+, Firefox, Chrome, Opera, Safari
    xmlhttp=new XMLHttpRequest();
  } else {  // code for IE6, IE5
    xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
  }
      
  xmlhttp.onreadystatechange=function() {on_server_response(xmlhttp);};
  xmlhttp.open(
    "GET", 
    "http://maps.googleapis.com/maps/api/geocode/json?address=" + str,
    true);
  xmlhttp.send();
}

//////////////////////////////////////////////////////////
// Responses /////////////////////////////////////////////    
//////////////////////////////////////////////////////////

function on_server_response(xmlhttp){
  if (xmlhttp.readyState==4 && xmlhttp.status==200) {
    var jsonData = JSON.parse(xmlhttp.responseText);

    if(jsonData['type'] == 'FeatureCollection') {
      clearTimeout(map_data_request_timeout_timer);
      map_data_request_counter = 0;
      status_box = document.getElementById("status_box");
      status_box.innerHTML = "Hover on a disk to display providers avilable at location. Click on a name to get available procedures. Disk size reflects "
      if(jsonData['procedure'] == 'all'){
        status_box.innerHTML = status_box.innerHTML + "average expensiveness.";
      }
      else{
        status_box.innerHTML = status_box.innerHTML + "price for procedure: " + jsonData['procedure'] + ".";
      }
      map.data.forEach(function(feature){map.data.remove(feature);});
      map.data.addGeoJson(jsonData);
      infowindow.close();
    }
    else if(jsonData['type'] == 'ProcedureList'){
      clearTimeout(procedure_request_timeout_timer);
      procedure_request_counter = 0;
      fill_in_procedure_table(jsonData);
    }
    else if(jsonData['type'] == 'ProviderList'){
      clearTimeout(provider_request_timeout_timer);
      provider_request_counter = 0;
      fill_in_provider_table(jsonData);
    }
    else if('results' in jsonData){
      if(jsonData['results'].length > 0){
        var blurb = jsonData['results'][0];
        var n_comp = blurb["address_components"].length;
        var state = blurb["address_components"][n_comp - 2]["short_name"];
        if(state == "MA"){
          var latitude = blurb["geometry"]["location"]["lat"];
          var longitude = blurb["geometry"]["location"]["lng"];
          var location = new google.maps.LatLng(latitude, longitude);
          map.panTo(location);
        }
        else{
          document.getElementById("status_box").innerHTML = "Only Massachusetts is currently supported.";
        }
      }
      else{
        document.getElementById("status_box").innerHTML = "Google is unable to parse the location.";
      }
      
    }
  }
}

function fill_in_procedure_table(jsonData){
  
  var provider = jsonData['provider'];
  var title = document.getElementById('info_title');
  if(provider["npi"] == 0){
    title.innerHTML = "No provider selected: displaying average values for MA"
  }
  else {
    title.innerHTML = "Procedures provided by " + provider["first_name"] + " " + provider["last_name"]
    if(provider["credentials"] != ""){
      title.innerHTML = title.innerHTML + ", " + provider["credentials"];
    }
     title.innerHTML = title.innerHTML + ":"
    
  }
  
  if(selected_procedure_index >= 0){
    procedure_list = [procedure_list[selected_procedure_index]];
    
    selected_procedure_index = 0;
    procedure_list = procedure_list.concat(jsonData['procedures']);
    for(i = 1; i < procedure_list.length; i++){
      if(procedure_list[i][0] == procedure_list[0][0]){
        procedure_list[0] = procedure_list[i];
        procedure_list.splice(i, 1);
      }
    }
  }
  else
      procedure_list = jsonData['procedures'];
      
  
  
  var table = document.getElementById('procedure_table');
  while(table.rows.length > 1){
    table.deleteRow(1);
  }
  
  for(i = 0; i < procedure_list.length; i++){
    row = table.insertRow(i + 1);
    if(i == selected_procedure_index){
      row.setAttribute("id", "selected_row");
    }
    row.setAttribute("onclick", "on_item_click(this)");
    
    cell = row.insertCell(0);
    cell.innerHTML = procedure_list[i][0];
    
    cell = row.insertCell(1);
    cell.innerHTML = procedure_list[i][1];
    
    cell = row.insertCell(2);
    cell.innerHTML = "$ " + procedure_list[i][4].toFixed(2);
    
    cell = row.insertCell(3);
    cell.innerHTML = "$ " + procedure_list[i][3].toFixed(2);
    
    cell = row.insertCell(4);
    cell.innerHTML = procedure_list[i][2];
  }
}

function fill_in_provider_table(jsonData){
  
  providers_on_table = jsonData['providers'];
  
  var table = document.getElementById('provider_table');
  while(table.rows.length > 0){
    table.deleteRow(0);
  }

  for(i = 0; i <  providers_on_table.length; i++){
   
    row = table.insertRow(table.rows.length);
    row.setAttribute("onclick", "on_provider_table_click(" + i + ")");
    
    cell = row.insertCell(0);
    cell.innerHTML =  providers_on_table[i]["first_name"] + " " +
      providers_on_table[i]["last_name"];
    
    cell = row.insertCell(1);
    cell.innerHTML =  providers_on_table[i]["street1"];
    
    cell = row.insertCell(2);
    cell.innerHTML =  providers_on_table[i]["city"];
    
    cell = row.insertCell(3);
    cell.innerHTML =  providers_on_table[i]["state"];
    }
}

//////////////////////////////////////////////////////////
// Events ////////////////////////////////////////////////    
//////////////////////////////////////////////////////////

// Map related ///////////////////////////////////////////

function on_bounds_changed(){
  
  ne_lat = map.getBounds().getNorthEast().lat(),
  ne_lng = map.getBounds().getNorthEast().lng(),
  sw_lat = map.getBounds().getSouthWest().lat(),
  sw_lng = map.getBounds().getSouthWest().lng();
//   var dump = document.getElementById("dump");
  
  if(bounds_changed_timeout){
    clearTimeout(bounds_changed_timeout);
//     dump.innerHTML = dump.innerHTML + "<br/>" + "clear Timeout";
  }
  bounds_changed_timeout = setTimeout(request_map_data, 500);
//   dump.innerHTML = dump.innerHTML + "<br/>" + "set Timeout";
}

function on_marker_mouseover(event){
  infowindow_providers = event.feature.getProperty('providers');
  unit = event.feature.getProperty('unit');
  while (infowindow_selector.firstChild) {
    infowindow_selector.removeChild(infowindow_selector.firstChild);
  }
  if(infowindow_providers.length > 5){
    infowindow_selector.setAttribute("size", "5");
  }
  else if(infowindow_providers.length < 3){
    infowindow_selector.setAttribute("size", "2");
  }
  else
  {
    infowindow_selector.setAttribute("size", String(infowindow_providers.length));
  }
    
  for(i = 0; i < infowindow_providers.length; i++){
    option = document.createElement('option');
    infowindow_selector.appendChild(option);
    option.text = infowindow_providers[i]['last_name'] + ", " +
      infowindow_providers[i]['first_name'] + " " + unit +
    infowindow_providers[i]["expensiveness"].toFixed(2);
  }

  infowindow.setContent(infowindow_selector);
  infowindow.setPosition(event.latLng);
  infowindow.open(map);
}

function set_feature_style(feature){
    var radius = 5 * feature.getProperty('min_expensiveness');
    if(radius > 30){
      radius = 30
    }
    
    return {
      icon: {
        path: google.maps.SymbolPath.CIRCLE,
        strokeWeight: 1,
        fillOpacity: .5,
        fillColor: '#CC0066',
        strokeColor: '#660033',
        scale: radius
      }
    };
}

// Procedure selection related //////////////////////////

function on_procedure_search_keyup(str){
  if(str.length > 2 || str.length == 0){
    procedure_search_string = str;
    request_procedure_list();
 }
}

function clear_procedure_search(){
  var searchbox = document.getElementById("procedure_search");
  searchbox.value = "";
  procedure_search_string = "";
  request_procedure_list();
}
function on_item_click(row){
//   dump = document.getElementById("dump");
  if(row.id == "selected_row"){
    row.removeAttribute("id");
    selected_procedure_index = -1;
//     dump.innerHTML = selected_procedure_index;
  }
  else if(row.rowIndex > 0)
  {
    selected_row = document.getElementById("selected_row");
    if(selected_row)
      selected_row.removeAttribute("id");
    
    row.setAttribute("id", "selected_row");
    selected_procedure_index = row.rowIndex - 1;
//     dump.innerHTML = selected_procedure_index;
  }
  document.getElementById("status_box").innerHTML = "Waiting for data...";
  map.data.forEach(function(feature){map.data.remove(feature);});
  request_map_data();
}

// Provider selection related ///////////////////////////

function on_marker_click(event){
  providers = event.feature.getProperty('providers');
  on_select_provider(providers[0]);
}

function on_map_click(){
  on_select_provider({"npi": 0});
}

function on_infowindow_selector_change(selector){
  var i = selector.selectedIndex;
  on_select_provider(infowindow_providers[i]);
}

function on_select_provider(provider){
//   alert(JSON.stringify(provider));
  selected_provider = provider;
  request_procedure_list();
}

function on_provider_search_keyup(str){
  if(str.length > 2){
    provider_search_string = str;
    request_provider_list();
  }
}

function on_provider_table_click(i){
  var p = providers_on_table[i];
  var location = new google.maps.LatLng(p["latitude"], p["longitude"]);
  
  on_select_provider(p);
  
  map.panTo(location);
  provider_search_marker.setPosition(location);
  provider_search_marker.setMap(map);
  
  
}

function clear_provider_search(){
  var searchbox = document.getElementById("provider_search");
  searchbox.value = "";
  
  provider_search_string = "";
  provider_search_marker.setMap(null);
  var table = document.getElementById('provider_table');
  while(table.rows.length > 0){
    table.deleteRow(0);
  }
}

// Location selection related ///////////////////////////

function search_location(){
  str = document.getElementById("location_text_box").value;
  request_location(str);
}