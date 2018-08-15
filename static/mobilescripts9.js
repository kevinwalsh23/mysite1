// Google Map
var map;

// markers for map
var markers = [];

// info window
var info = new google.maps.InfoWindow();
i=1;

// execute when the DOM is fully loaded
$(function() {

    $(document).ready(function(){
       tabFunction();
    });

    $(window).resize(function(){
        tabFunction();
    });

    function tabFunction(){
        var windowWindth = $(window).width();
        if(windowWindth < 767){
            $('.tab-item').removeClass('show');
            $('.tab-item').removeClass('hide');
            $('.tab-menu ul li a').removeClass('active');

            $('.tab-menu ul li a').click(function(){
                var itemID = $(this).attr('data-id');
               $('.tab-item').addClass('hide');
               $('.tab-item').removeClass('show');
               $('.tab-menu ul li a').removeClass('active');
               $(this).addClass('active');

               if($('#'+itemID).hasClass('hide')){
                   $('#'+itemID).removeClass('hide').addClass('show');
               }
            });
        }else{
           $('.tab-item').removeClass('hide');
        }
    }

    // styles for map
    // https://developers.google.com/maps/documentation/javascript/styling
    var styles = [

        // hide Google's labels
        {
            featureType: "all",
            elementType: "labels",
            stylers: [
                {visibility: "on"}
            ]
        },

        // hide roads

    ];

    // options for map
    // https://developers.google.com/maps/documentation/javascript/reference#MapOptions
    var options = {
        center: {lat: 40.7280207, lng: -73.9941032}, // Empire State Building, NY
        disableDefaultUI: true,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        maxZoom: 20,
        panControl: true,
        styles: styles,
        zoom: 12.8,
        zoomControl: true
    };

    // get DOM node in which map will be instantiated
    var canvas = $("#map-canvas").get(0);

    // instantiate map
    map = new google.maps.Map(canvas, options);

    // configure UI once Google Map is idle (i.e., loaded)
    google.maps.event.addListenerOnce(map, "idle", configure);

    for (let m of markers) {
        addMarker(m);
    }



    // options for map
    //update();

   //google.maps.event.addListener(marker, "click", function() { loadInfoWindow(place, marker) });

}


);

/**
 * Adds marker for place to map.
 */

function addMarker(place)
{
   // var stuff = "http://maps.google.com/mapfiles/kml/pal3/icon40.png";
    var myLatLng = new google.maps.LatLng(parseFloat(place.latitude), parseFloat(place.longitude));

    var kmarker = new google.maps.Marker({
    position: myLatLng,
    map: map,
    title:  "Hello",
    labelContent:  "Goodbye",
    labelAnchor: new google.maps.Point(27, 60),
    labelClass: "labels",
    //icon: icon
  });

   //google.maps.event.addListener(marker, "click", function() { loadInfoWindow(place, marker) });

   // markers.push(kmarker);

        jeff = "https://www.google.com/maps/dir//" + place.bar_name;

        google.maps.event.addListener(kmarker, "click", function() {
        var news =  place.bar_name + " " + '<div>' + place.address + '</div>' + place.city + ", " + place.state + " " + place.zip + '<div>' + '<a href="https://www.google.com/maps/dir//'+place.bar_name +'">Directions Here'+ '</a>' + '</div>' ;
        //for (var i = 0; i < 5; i++){
        //news += "<li><a href=' " + data[i] + "'>" + data[i]["title"] + "</a></li>";
    //}
    //news += "</ul>";

    showInfo(kmarker, news);

});
i++;


function showInfo(marker, content)
{
    // start div
    var div = "<div id='info'>";
    if (typeof(content) == "undefined")
    {
        // http://www.ajaxload.info/
        div += "<img alt='loading' src='/static/ajax-loader.gif'/>";
    }
    else
    {
        div += content;
    }

    // end div
    div += "</div>";

    // set info window's content
    info.setContent(div);

    // open info window (if not already open)
    info.open(map, marker);
}

}

function removeMarkers()
{
    var lentil_markers = markers.length;
    for (var i = 0; i < lentil_markers; i++){
        markers[i].setMap(null);
    }

    markers.length = 0;
    // TODO
}

function configure()
{
    // update UI after map has been dragged
    google.maps.event.addListener(map, "dragend", function() {

        // if info window isn't open
        // http://stackoverflow.com/a/12410385
        if (!info.getMap || !info.getMap())
        {
            update();
        }
    });

    // update UI after zoom level changes
    google.maps.event.addListener(map, "zoom_changed", function() {
        update();
    });



   // update();
}



function update()
{
    $.getJSON(Flask.url_for("mapadd"))
    .done(function(data, textStatus, jqXHR) {

        console.log('hello where am i ', data);

       // remove old markers from map
       removeMarkers();

       // add new markers to map
       for (var i = 0; i < data.length; i++)
       {
           addMarker(data[i]);
       }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.log('what is this', jqXHR);
        // log error to browser's console
        console.log(errorThrown.toString());
    });

}





$(document).ready(
    function(){
        $("#search").click(function () {
            $("#searchoption").toggle();
        });
    });
$(document).ready(
    function(){
        $('.mininterval').each(function(index) {
            var min = $('#seconds')[0].innerHTML;
            var max = $('.mininterval')[index].innerHTML;
            console.log(max);
            console.log(min);
            if ((max - min) <= 60) {
                console.log(max - min);
                $('.mininterval').eq(index).html("Ending in " + (max-min) +" minutes !");
                $('.mininterval').eq(index).css("color", "red");
                $('.mininterval').eq(index).show();

            }
            else if ((max - min) <= 120) {
                console.log(max - min);
                $('.mininterval').eq(index).html("Ending in less than two hours!");
                $('.mininterval').eq(index).css("color", "orange");
                $('.mininterval').eq(index).show();

            }

        });
    });
//var theForm = document.getElementsById("form")[0];

//$.ajax({
//           type: "POST",
//           url : Flask.url_for("mapadd"),
  //         data: $(theForm).serialize(), // <-- Inject serialized form data
    //       success: function(msg){
      //           // get response here
        //       }
          // });

//$("button#submit").click(function() {
  //  $.post(Flask.url_for("mapadd"), $("form#form").serialize(), function(data){
        //DO something
    //});

    //$.post(Flask.url_for("indexsearch"), $('form#form').serialize(), function(data){
        //DO something
  //  });
//});
//function passvalidate() {
 //   var x, y, text;

    // Get the value of the input field with id="numb"
//    x = document.getElementById("numb").value;
  //  y = document.getElementById("numb").value;

    // If x is Not a Number or less than one or greater than 10
    //if (x != y) {
      //  text = "passwords much match";
    //}

//    document.getElementById("demo").innerHTML = text;
//}