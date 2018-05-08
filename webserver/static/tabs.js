// handles js
$(document).ready(function()
{
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

function bindSlider(sliderID, textID, name, params)
{
	$("#" + sliderID).on("slide", function(slideEvt) {
		// get request to Flask server
		var obj = {};
		var str = "";
		// convert single value to array if necessary
		var value = slideEvt.value;
		if (value.constructor !== Array)
		{
			value = [value];
		}
		// create string and params
		for (var i = 0; i < params.length; i++)
		{
			obj[params[i]] = value[i];
			if (i > 0)
			{
				str += "-";
			}
			str += value[i];
		}
		// send request to flask server
		$.get("/fuck?" + $.param(obj)).done(sliderDone).fail(sliderFail);
		// set text
		$("#" + textID).text(name + ": " + str);
	});
}