var sBrowser, sUsrAg = navigator.userAgent;



if (sUsrAg.indexOf("MSIE") > -1) {
  sBrowser = "Microsoft Internet Explorer";
  

  alert("You are using " + sBrowser + ". Unfortunately, Stencila Hub does not support this browser. Please use Chrome, Safari or Firefox."); 
}

