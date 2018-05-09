// handles js
$(document).ready(function() {

	// link pixel buttons to set variables
	bindPixelButton("eyedropper");
	bindPixelButton("add-pixel");
	bindPixelButton("subtract-pixel");
	bindPixelButton("calibrate-xy-a");
	bindPixelButton("calibrate-x-a");
	bindPixelButton("calibrate-y-a");
	bindPixelButton("calibrate-xy-b");
	bindPixelButton("calibrate-x-b");
	bindPixelButton("calibrate-y-b");
	// handle eyedropper/add/subtract clicks on the stream
	$("#stream").click(function(event) {
		// check for eyedropper
		if (pixelButtons["eyedropper"])
		{
			pixelButtonSend(event, "eyedropper");
		}
		if (pixelButtons["add-pixel"])
		{
			pixelButtonSend(event, "add");
		}
		if (pixelButtons["subtract-pixel"])
		{
			pixelButtonSend(event, "subtract");
		}

		var center = [160, 120];
		// calibration buttons A
		if (pixelButtons["calibrate-xy-a"])
		{
			pixelButtonSend(event, "cross_a", "fuck", ["x", "y"], ["_x", "_y"], center);
		}
		if (pixelButtons["calibrate-x-a"])
		{
			pixelButtonSend(event, "cross_a", "fuck", ["x"], ["_x"], center);
		}
		if (pixelButtons["calibrate-y-a"])
		{
			pixelButtonSend(event, "cross_a", "fuck", ["y"], ["_y"], center);
		}

		// calibration buttons B
		if (pixelButtons["calibrate-xy-b"])
		{
			pixelButtonSend(event, "cross_b", "fuck", ["x", "y"], ["_x", "_y"], center);
		}
		if (pixelButtons["calibrate-x-b"])
		{
			pixelButtonSend(event, "cross_b", "fuck", ["x"], ["_x"], center);
		}
		if (pixelButtons["calibrate-y-b"])
		{
			pixelButtonSend(event, "cross_b", "fuck", ["y"], ["_y"], center);
		}
	});

	// only show dual crosshair mode when selected
	$("#xhair-select").change(function() {
		switch ($(this)[0].selectedIndex)
		{
			// if option 0, single crosshair, hide B and change Crosshair A to Crosshair
			case 0:
				$("#xhair-calibration-a").text("Crosshair");
				$("#crosshair-b").hide();
				break;
			// if option 1, single crosshair, dual crosshair, show B and change Crosshair to Crosshair A
			case 1:
				$("#xhair-calibration-a").text("Crosshair A");
				$("#crosshair-b").show();
				break;
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
	});
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

	// make the reset buttons reset the xhair offsets
	$("#calibrate-reset-a").click(function(event) {
		$.get("/fuck?" + $.param({cross_a_x: 0, cross_a_y: 0})).done(sliderDone).fail(sliderFail);
	});
	$("#calibrate-reset-b").click(function(event) {
		$.get("/fuck?" + $.param({cross_b_x: 0, cross_b_y: 0})).done(sliderDone).fail(sliderFail);
	});

	// make the snapshot button take a snapshot
	$("#snapshot").click(function(event) {
		$.get("/the_actual_fuck?" + $.param({snapshot: true})).done(sliderDone).fail(sliderFail);
	});

	// set default pipeline
	$("#pipeline-default").click(function(event) {
		$.get("/app_prefs?" + $.param({default_pipeline: $("#pipeline-select")[0].selectedIndex})).done(sliderDone).fail(sliderFail);
	});

	// download the current pipeline
	$("#pipeline-download").click(function(event) {
		$.get("/fuck").done(function(data) {
			download("prefs" + $("#pipeline-select")[0].selectedIndex + ".vpr2", JSON.stringify(JSON.parse(data), null, 4));
		}).fail(sliderFail);
	});

	// download the current pipeline
	$("#pipeline-upload").click(function(event) {
		$("#file-upload").click();
	});
	$("#file-upload").click(function(event) {
	});
	$("#file-upload").change(function(event) {
		event.preventDefault();
		var formData = new FormData($("#form-upload")[0]);
		$.ajax({
			url: "the_actual_fuck",
			type: "POST",
			data: formData,
			success: function (data) {
			},
			cache: false,
			contentType: false,
			processData: false
		});
		$("#file-upload").val("");
	});
	$("#form-upload").submit(function(event) {
		event.preventDefault();
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
		$.get("/app_prefs?" + $.param({ignore_nt: this.checked})).done(sliderDone).fail(sliderFail);
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
	bindDropdown("source-select", "source", "the_actual_fuck");
	bindDropdown("orientation-select", "image_flip");
	bindDropdown("feed-select", "view_mode", "app_prefs");
	bindDropdown("erosion-select", "erosion");
	bindDropdown("dilation-select", "dilation");
	bindDropdown("sorting-select", "contour_sort_final");
	bindDropdown("region-select", "desired_contour_region");
	bindDropdown("grouping-select", "contour_grouping");
	bindDropdown("xhair-select", "calibration_type");

	// handle pipeline choose dropdown
	$("#pipeline-select").change(function() {
		var obj = {};
		obj["current_pipeline"] = $(this)[0].selectedIndex;
		// send request to flask server
		$.get("/app_prefs?" + $.param(obj)).done(loadPrefs).fail(loadPrefs);
	});

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

	// at start, ajax to app_prefs to get current pipeline/ignore_nt state
	// load prefs at end to make sure all bindings have occurred
	$.get("/fuck").done(function(data) {
		var obj = JSON.parse(data);
		$("#pipeline-select")[0].selectedIndex = obj.current_pipeline;
		$("#ignore-nt").prop('checked', obj.ignore_nt);
	});
	loadPrefs();
});

// slider callbacks
var sliderFail = function( jqXHR, textStatus, errorThrown ) {
	$("#result").html(textStatus);
}
var sliderDone = function( jqXHR, textStatus, errorThrown ) {
	$("#result").html(textStatus);
}

// binds a dropdown menu to output to the flask server
function bindDropdown(dropdownID, param, url = "fuck")
{
	$("#" + dropdownID).change(function() {
		// find args, paramName and dropdown value
		var obj = {};
		obj[param] = $(this)[0].selectedIndex;
		// send request to flask server
		$.get("/" + url + "?" + $.param(obj)).done(sliderDone).fail(sliderFail);
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
		var value = $("#" + sliderID).slider("getValue");
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
function pixelButtonSend(event, name, url = "the_actual_fuck", dimensions = ["x", "y"], params = ["X", "Y"], origin = [0, 0])
{
	// get click position
	var offset = $(event.target).offset();
	var x = event.pageX - offset.left;
	var y = event.pageY - offset.top;
	// convert to 320x240
	var size = {x: $(event.target).width(), y: $(event.target).height()};
	var pos = {x: -origin[0], y: -origin[1]};
	if (size.x > 0 && size.y > 0)
	{
		pos.x += x * 320 / size.x;
		pos.y += y * 240 / size.y;
	}
	// send get request
	var obj = {};
	for (var i = 0; i < params.length; i++)
	{
		obj[name + params[i]] = pos[dimensions[i]];
	}
	$.get("/" + url + "?" + $.param(obj)).done(sliderDone).fail(sliderFail);
}

// gets current pipeline data from server and loads in
function loadPrefs()
{
	$.get("/fuck").done(setPrefs).fail(sliderFail);
}

// sets UI data, loaded from pipeline.
function setPrefs(data) {
	// parse json to data object
	var obj = JSON.parse(data);
	// input: camera orientation, exposure, rbalance, bbalance
	$("#orientation-select")[0].selectedIndex = obj.image_flip;
	setSlider("expSlider", obj.exposure);
	setSlider("rbalSlider", obj.red_balance);
	setSlider("bbalSlider", obj.blue_balance);
	// thresholding: hue, saturation, value
	setSlider("hueThreshold", [obj.hue_min, obj.hue_max]);
	setSlider("satThreshold", [obj.sat_min, obj.sat_max]);
	setSlider("valThreshold", [obj.val_min, obj.val_max]);
	// contour filtering: sorting, area, fullness, aspect ratio
	$("#sorting-select")[0].selectedIndex = obj.contour_sort_final;
	setSlider("areaFilter", [obj.area_min, obj.area_max], function(x) { return Math.round(100 * Math.pow(x / 100, 0.25)); });
	setSlider("fullFilter", [obj.convexity_min, obj.convexity_max]);
	setSlider("aspectFilter", [obj.aspect_min, obj.aspect_max], function(x) { return Math.round(100 * Math.pow(x / 100, 0.5)); });
	// output: region, grouping, crosshair mode
	$("#region-select")[0].selectedIndex = obj.desired_contour_region;
	$("#grouping-select")[0].selectedIndex = obj.contour_grouping;
	$("#xhair-select")[0].selectedIndex = obj.calibration_type;
	// trigger change to xhair-select
	$("#xhair-select").trigger("change");
}

// download a file with the given text
function download(filename, text) {
	var element = document.createElement('a');
	element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
	element.setAttribute('download', filename);

	element.style.display = 'none';
	document.body.appendChild(element);

	element.click();

	document.body.removeChild(element);
}

// allows you to set a slider and update it
function setSlider(sliderID, value, inverse = function(x) { return x; })
{
	// apply inverse, preserving array if necessary
	if (value.constructor === Array)
	{
		for (var i = 0; i < value.length; i++)
		{
			value[i] = inverse(value[i]);
		}
	}
	else
	{
		value = inverse(value);
	}
	// set slider
	$("#" + sliderID).slider("setValue", value);
	$("#" + sliderID).trigger("slide");
}