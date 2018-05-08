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
		console.log("running");
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
			console.log("running0");
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
	
	// slider callbacks
	var sliderFail = function( jqXHR, textStatus, errorThrown ) {
		$("#result").html(textStatus);
	}
	var sliderDone = function( jqXHR, textStatus, errorThrown ) {
		$("#result").html(textStatus);
	}

	// handle slider drag
	$("#hueThreshold").on("slide", function(slideEvt) {
		$("#hueText").text("Hue: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { hue_min: slideEvt.value[0], hue_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params)).done(sliderDone).fail(sliderFail);
	});
	$("#satThreshold").on("slide", function(slideEvt) {
		$("#satText").text("Saturation: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { sat_min: slideEvt.value[0], sat_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params)).done(sliderDone).fail(sliderFail);s
	});
	$("#valThreshold").on("slide", function(slideEvt) {
		$("#valText").text("Value: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { val_min: slideEvt.value[0], val_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params)).done(sliderDone).fail(sliderFail);
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
});