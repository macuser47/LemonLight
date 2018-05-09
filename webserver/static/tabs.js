// handles js
$(document).ready(function()
{
	// link pixel buttons to set variables
	bindPixelButton("eyedropper");
	bindPixelButton("add-pixel");
	bindPixelButton("subtract-pixel");
	// handle eyedropper/add/subtract clicks on the stream
	$("#stream").click(function(event) {
		// check for eyedropper
		if (pixelButtons["eyedropper"])
		{
			pixelButtonSend(event, "eyedropper");
		}
		else if (pixelButtons["add-pixel"])
		{
			pixelButtonSend(event, "add");
		}
		else if (pixelButtons["subtract-pixel"])
		{
			pixelButtonSend(event, "subtract");
		}
	});

	// hide the pipeline form at start
	$("#pipeline-form").hide();
	// allow user to rename the pipeline
	$("#pipeline-name").mouseenter(function(event) {
		$(this).css("background-color", "#ADD8E6");
	}).mouseleave(function(event) {
		$(this).css("background-color", "transparent");
	});
	// handle changing the pipeline name
	// on click, turn name into a text field
	$("#pipeline-name").click(function(event) {
		$("#pipeline-form").val($("#pipeline-name").text().trim());
		$("#pipeline-name").hide();
		$("#pipeline-form").show();
		$("#pipeline-form").select();
		event.stopPropagation();
	})
	// on click outside, then set the text field to the name
	$(document).click(function(event)
	{
		// if pipeline form is visible, meaning that the user entered a pipeline name
		if ($("#pipeline-form").is(":visible"))
		{
			var container = $("#pipeline-form");
			// if the target of the click is outside the pipeline-form element
			if (!container.is(event.target) && container.has(event.target).length === 0) 
			{
				// set the pipeline name to the form value
				if ($("#pipeline-form").val().trim() != "")
				{
					$("#pipeline-name").text($("#pipeline-form").val().trim());
					$("#pipeline-name").show();
					$("#pipeline-form").hide();
				}
			}
		}
	});
	// enter does the same thing as on click outside
	$('#pipeline-form').keypress(function (event) {
		// if enter is pressed
		var key = event.which;
		if(key == 13)
		{
			// simulate a click outside
			$(document).click();
		}
	});

	// make the user unable to edit the pipeline if the ignore checkbox is checked
	$("#ignore-nt").change(function(){
		if (this.checked)
		{
			$("#pipeline-select").attr("disabled", true);
		}
		else
		{
			$("#pipeline-select").removeAttr("disabled");
		}
	});

	// make buttons rounded squares
	$(".slider-handle").removeClass("round").addClass("rounded");
	// make sliders fill divs
	$(".slider.slider-horizontal").css("margin-left", "1.2%");
	$(".slider.slider-horizontal").css("width", "97%");

	// handle thresholding slider drag
	bindSlider("expSlider", "expText", "Exposure", ["exposure"]);
	bindSlider("rbalSlider", "rbalText", "Red Balance", ["red_balance"]);
	bindSlider("bbalSlider", "bbalText", "Blue Balance", ["blue_balance"]);
	bindSlider("hueThreshold", "hueText", "Hue", ["hue_min", "hue_max"]);
	bindSlider("satThreshold", "satText", "Saturation", ["sat_min", "sat_max"]);
	bindSlider("valThreshold", "valText", "Value", ["val_min", "val_max"]);
	bindSlider("areaFilter", "areaText", "Target Area (% of image)", ["area_min", "area_max"], function(x) { return 100 * Math.pow(x / 100, 4); });
	bindSlider("fullFilter", "fullText", "Target Fullness (% of bounding rectangle)", ["convexity_min", "convexity_max"]);
	bindSlider("aspectFilter", "aspectText", "Target Aspect Ratio (W/H)", ["aspect_min", "aspect_max"], function(x) { return 20 * Math.pow(x / 20, 2); });

	// handle dropdown menus
	bindDropdown("source-select", "image_source");
	bindDropdown("orientation-select", "image_flip");
	bindDropdown("feed-select", "feed");
	bindDropdown("erosion-select", "erosion");
	bindDropdown("dilation-select", "dilation");
	bindDropdown("sorting-select", "contour_sort_final");

	// handle tab clicks
	$('.nav-linktabs > li > a').click(function(event) {

		//stop browser to take action for clicked anchor
		event.preventDefault();

		var clickedTab = $(event.currentTarget);
		var otherTabs = clickedTab.parent().siblings().children();

		// set all sibling tabs to inactive
		otherTabs.removeClass("active");

		// set target tab to active
		clickedTab.addClass("active");

		// get div to activate
		var activeDiv = clickedTab.attr("href");

		// for each sibling, hide div if it's not the target
		otherTabs.each(function() {
			var targetDiv = $(this).attr("href");
			var section = $("section" + "#" + targetDiv);
			section.hide();
		});

		// show the clicked one
		var section = $("section" + "#" + activeDiv);
		section.show();
	});
});

// slider callbacks
var sliderFail = function( jqXHR, textStatus, errorThrown ) {
	$("#result").html(textStatus);
}
var sliderDone = function( jqXHR, textStatus, errorThrown ) {
	$("#result").html(textStatus);
}

// binds a dropdown menu to output to the flask server
function bindDropdown(dropdownID, param)
{
	$("#" + dropdownID).change(function() {
		// find args, paramName and dropdown value
		var obj = {};
		obj[param] = $(this)[0].selectedIndex;
		// send request to flask server
		$.get("/fuck?" + $.param(obj)).done(sliderDone).fail(sliderFail);
	});
}

// binds a slider to output to the flask server
function bindSlider(sliderID, textID, name, params, conversion = function(x) { return x; })
{
	$("#" + sliderID).on("slide", function(event) {
		// get request to Flask server
		var obj = {};
		var str = "";
		// convert single value to array if necessary
		var value = event.value;
		if (value.constructor !== Array)
		{
			value = [value];
		}
		// create string and params
		for (var i = 0; i < params.length; i++)
		{
			var cvalue = conversion(value[i]);
			// round value to 5 sig figs
			if (cvalue > 1)
			{
				cvalue = parseFloat(cvalue.toFixed(4 - Math.floor(Math.log10(cvalue))));
			}
			else
			{
				cvalue = parseFloat(cvalue.toFixed(4));
			}
			obj[params[i]] = cvalue;
			if (i > 0)
			{
				str += "-";
			}
			str += cvalue;
		}
		// send request to flask server
		$.get("/fuck?" + $.param(obj)).done(sliderDone).fail(sliderFail);
		// set text
		$("#" + textID).text(name + ": " + str);
	});
}

// we can't use .is(":focus") directly on the click, since that will be reset before the event
// so instead we store the value until the click event fires, then reset it
var pixelButtons = {};
function bindPixelButton(buttonID)
{
	pixelButtons[buttonID] = false;
	$(document).click(function(event) {
		pixelButtons[buttonID] = $("#" + buttonID).is(":focus");
	});
}
// send a request from a pixel button when the stream is clicked on
function pixelButtonSend(event, name)
{
	// get click position
	var offset = $(event.target).offset();
	var x = event.pageX - offset.left;
	var y = event.pageY - offset.top;
	// convert to 320x240
	var size = {x: $(event.target).width(), y: $(event.target).height()};
	var pos = {x: 0, y: 0};
	if (size.x > 0 && size.y > 0)
	{
		pos.x = x * 320 / size.x;
		pos.y = y * 240 / size.y;
	}
	// send get request
	var obj = {};
	obj[name + "X"] = pos.x;
	obj[name + "Y"] = pos.y;
	$.get("/the_actual_fuck?" + $.param(obj)).done(sliderDone).fail(sliderFail);
}