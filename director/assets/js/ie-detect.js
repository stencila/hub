var sBrowser, sUsrAg = navigator.userAgent;

Vue.component('modal', {
    template: '#modal-template'
  })

if (sUsrAg.indexOf("MSIE") > -1) {
  sBrowser = "Microsoft Internet Explorer";
  new Vue({
    el: '#app',
   showModal: true
    }
  ) 

//  document.write("You are using " + sBrowser + ". Unfortunately, Stencila Hub does not support this browser. Please use Chrome, Safari or Firefox."); 
}

