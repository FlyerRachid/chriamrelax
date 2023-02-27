
const phoneInputField = document.querySelector("#phone");
console.log('phoneInputField ',phoneInputField);
const phoneInput = window.intlTelInput(phoneInputField, {
      preferredCountries: ["BE", "FR", "MA"],
      utilsScript:
        "https://cdnjs.cloudflare.com/ajax/libs/intl-tel-input/17.0.8/js/utils.js",
    });

 const info  = document.querySelector(".alert-info");
 const error = document.querySelector(".alert-error");
    
    
 function process(event) {
 
 console.log(event);
 
 event.preventDefault();

 const phoneNumber = phoneInput.getNumber();

 info.style.display = "none";
 error.style.display = "none";

	 if (phoneInput.isValidNumber()) {
	   info.style.display = "";
	   info.innerHTML = `Phone number in E.164 format: <strong>${phoneNumber}</strong>`;
	 } else {
	   error.style.display = "";
	   error.innerHTML = `Invalid phone number.`;
	 }
}


//https://www.twilio.com/fr/blog/saisie-numeros-telephone-internationaux-html-javascript
//https://ipinfo.io/account/home
//fn + s screenshot
 