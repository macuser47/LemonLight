// handles linktab system
$(document).ready(function() {
	// make buttons rounded squares
	$(".slider-handle").removeClass("round").addClass("rounded");
	// make sliders fill divs
	$(".slider.slider-horizontal").css("margin-left", "1.2%");
	$(".slider.slider-horizontal").css("width", "97%");
	
	// handle slider drag
	$("#hueThreshold").on("slide", function(slideEvt) {
		$("#hueText").text("Hue: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { hue_min: slideEvt.value[0], hue_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params))
			.done(function( data, textStatus, jqXHR ) {
				$("#result").html(data);
			})
			.fail(function( jqXHR, textStatus, errorThrown ) {
				$("#result").html(textStatus);
			});
	});
	$("#satThreshold").on("slide", function(slideEvt) {
		$("#satText").text("Saturation: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { sat_min: slideEvt.value[0], sat_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params))
			.done(function( data, textStatus, jqXHR ) {
				$("#result").html(data);
			})
			.fail(function( jqXHR, textStatus, errorThrown ) {
				$("#result").html(textStatus);
			});
	});
	$("#valThreshold").on("slide", function(slideEvt) {
		$("#valText").text("Value: " + slideEvt.value[0] + "-" + slideEvt.value[1]);
		// get request to Flask server
		var params = { val_min: slideEvt.value[0], val_max: slideEvt.value[1] };
		$.get("/fuck?" + $.param(params))
			.done(function( data, textStatus, jqXHR ) {
				$("#result").html(data);
			})
			.fail(function( jqXHR, textStatus, errorThrown ) {
				$("#result").html(textStatus);
			});
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