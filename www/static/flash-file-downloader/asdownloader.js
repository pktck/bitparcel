/*
 * ASDownloader
 */

var ASDownloader = {};

ASDownloader.misc = {};

/******************************************/
ASDownloader.flashPath = 'asdownloader.swf';
ASDownloader.flashContainer = 'flashContainer';
ASDownloader.lastResult = undefined;

/******************************************/
// Internal variables, do not meddle.

ASDownloader.networkReady = true;
ASDownloader.JSReady = false;
ASDownloader.ready = false;

ASDownloader.download = function(url, callback) {
	if (! ASDownloader.ready) { 
		return setTimeout(function() { ASDownloader.download(url, callback); }, 500);
	}

	ASDownloader.ready = false;

	if (! ASDownloader.misc.isFlashAvailable()) {
		alert("Sorry, we need Flash to proceed");
	}

	ASDownloader._url = url;
	ASDownloader._download(ASDownloader._url, callback);
}

/*********************************************************************************************/
// Misc. utility functions

ASDownloader_isJavaScriptReady = function() {
	return ASDownloader.JSReady;
}

ASDownloader.misc.quietEmbedSWF = function(path, containerEl) {
	var swfName = ASDownloader.misc.fileBasename(path);
	
	ASDownloader.misc.addInvisibleElement(swfName, containerEl);

	var params = { allowScriptAccess : "always", name : swfName };
	var flashvars = false;
	var attributes = { name : swfName};

	// TODO: remove this for production
	swfobject.embedSWF(path + '?' + ASDownloader.misc.getTime(), swfName, "148", "46", "10.0.0",
		"expressInstall.swf", flashvars, params, attributes);
}

ASDownloader.misc.addInvisibleElement = function(id, containerEl) {
	var container = document.getElementById(containerEl) || containerEl || document.body;

	if (!container) {
		return setTimeout(function() { ASDownloader.misc.addInvisibleElement(id, containerEl); }, 500);
	}

	if (document.getElementById(id)) {
		return false;
	}

	var elementType = 'div';

	var innerContainer = document.getElementById('browser_asdownloader_container');
	if (!innerContainer) {
		innerContainer = document.createElement('div');
		innerContainer.id = 'browser_asdownloader_container';
		innerContainer.style.display = 'none';
		container.appendChild(innerContainer);
	}
	// var innerContainer = document.getElementById('browser_asdownloader_container');

	var el = document.createElement(elementType);
	el.id = id;
	el.style.display = 'none';
	container.appendChild(el);

	return true;
}

ASDownloader.misc.fileBasename = function(path) {
	var s = path.replace(/.*\//, '').replace(/.swf/i, '');
	return s;
}

ASDownloader.misc.getMovie = function(movieName) { 
 
	if (navigator.appName.indexOf("Microsoft") != -1) { 
		return window[movieName];
	} else { 
		return document[movieName]; 
	} 
} 

ASDownloader.misc.handleResult = function(resultObj) {

	ASDownloader.lastResult = resultObj;

	// Clear queue of other methods if 
	if (!resultObj.error()) {
		ASDownloader.ready = true;
		
		// Execute user function on object here
		if (ASDownloader._handler) {
			ASDownloader._handler(resultObj);
		}
	} else {
		// nothing worked, return last result
		ASDownloader.ready = true;

		// Execute user function on object here
		if (ASDownloader._handler) {
			ASDownloader._handler(resultObj);
		}
	}
}

// This function gets called from ActionScript after the download is finished
ASDownloader.misc.sendToJavaScript = function(params) {
	// console.log(params);

	ASDownloader.networkReady = true;

	result = new ASDownloader.result(params);
	ASDownloader.misc.handleResult(result);
}

ASDownloader.misc.sendTimestampToFlash = function () {
	var timestamp = new Date().getTime() + "";
	ASDownloader.misc.getMovie("asdownloader").uploadTimestamp(timestamp);
}

ASDownloader.misc.getTime = function() {
	return (new Date()).getTime();
}

ASDownloader.misc.sendToActionScript = function(command) {
	if (!ASDownloader.networkReady) {
		return setTimeout(function() { ASDownloader.misc.sendToActionScript(command)}, 500);
	}
	
	ASDownloader.networkReady = false;
	ASDownloader.misc.getMovie("asdownloader").sendToActionScript(command);
}

ASDownloader.misc.isFlashAvailable = function() {
	if (navigator.mimeTypes && navigator.mimeTypes["application/x-shockwave-flash"])
		return true;
	else if (ASDownloader.isFlashReady())
		return true;
	else if (window.ActiveXObject) {
		for (x = 7; x <= 11; x++) {
			try {
				oFlash = eval("new ActiveXObject('ShockwaveFlash.ShockwaveFlash." + x + "');");
				if (oFlash) {
					return true;
				}
			}
			catch(e) { }
		}
	}
	else
		return false;
}

ASDownloader.misc.addOnloadEvent = function(newEvent) {
	var originalEvent = window.onload;

	if (typeof window.onload != 'function') {
		window.onload = newEvent;
	} else {
		window.onload = function() {
			if (originalEvent) { originalEvent(); }
			newEvent();
		}
	}
}

ASDownloader.misc.onloadActions = function () {
	ASDownloader.networkReady = true;
	ASDownloader.JSReady = true;
	ASDownloader.ready = true;
	
	ASDownloader.misc.quietEmbedSWF(ASDownloader.flashPath, ASDownloader.flashContainer);
}

ASDownloader.misc.log = function() {
	if (typeof(console) != "undefined" && console.log)
		console.log(arguments);
}

ASDownloader.isFlashReady = function() {
	var m = ASDownloader.misc.getMovie("asdownloader");
	return m && m.sendToActionScript;
}

ASDownloader._download = function (url, callback) {
	// Callbacks implemented: success, failure, progress
	if (!callback) {
		callback = {}
	} 

	var defaultHandler = ASDownloader.misc.log;
	ASDownloader.progressHandler = callback.progress || defaultHandler;
	ASDownloader.successHandler = callback.success || defaultHandler;
	ASDownloader.failureHandler = callback.failureHandler || defaultHandler;

	ASDownloader.misc.getMovie("asdownloader").download(url);
	ASDownloader.misc.getMovie("asdownloader").addCallback('progress', 'ASDownloader.progressHandler');
	ASDownloader.misc.getMovie("asdownloader").addCallback('success', 'ASDownloader.successHandler');
	ASDownloader.misc.getMovie("asdownloader").addCallback('failure', 'ASDownloader.failureHandler') ;
}

/* Create our container element */
document.write('<div id="browser_asdownloader_container"></div>');
ASDownloader.misc.addOnloadEvent(ASDownloader.misc.onloadActions);

