//alert('Odoo Js <+> ..*.. <+>');

data = []

function generateToken() {

      var pass = '';
      var str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' +
              'abcdefghijklmnopqrstuvwxyz0123456789@#$';
      for (i = 1; i <= 30; i++) {
          var char = Math.floor(Math.random()
                      * str.length + 1);

          pass += str.charAt(char)
      }
      return pass;
    }


function open_modalRequest(info) {
  document.getElementById('btn_modalRequest').click();
  data = []
  var token = info.event.extendedProps.token
  data.push(token);
  console.log(data);
 
}



function sendRequest(info) {
    
      //alert("Sending request ....",data[0]);
      
      var formData = new FormData();
      var http     = new XMLHttpRequest();

      const tab = data;

      var token = tab[0];
    
      var partner_name    = document.getElementById('partner_name').value;
      var partner_email   = document.getElementById('partner_email').value;
      var partner_phone   = phoneInput.getNumber() || document.getElementById('phone').value;
      var partner_street  = document.getElementById('partner_street').value;
      var partner_zip     = document.getElementById('partner_zip').value;
      var partner_country = document.getElementById('partner_country').value;
    
      formData.append('token'   ,token);
      formData.append('partner_name'    ,partner_name);
      formData.append('partner_email'   ,partner_email);
      formData.append('partner_phone'   ,partner_phone);
      formData.append('isValidNumber'   ,phoneInput.isValidNumber());
      formData.append('iso2'            ,phoneInput.getSelectedCountryData()['iso2']);
      formData.append('partner_street'  ,partner_street);
      formData.append('partner_zip'     ,partner_zip);
      formData.append('partner_country' ,partner_country);
    
      console.log(partner_phone,phoneInput.isValidNumber(),phoneInput.getSelectedCountryData()['iso2']);

      http.open('POST', '/request', true);

      http.onreadystatechange = function() {
          if((http.status == 200) && (http.readyState == 4)) {
              
           var json = JSON.parse(http.responseText);
           
           if (json.error == true){
               console.log('ERROR : ',json.error,json.html);
               document.getElementById('warning_request').style.display = "block";
               document.getElementById('warning_request').innerHTML     = json.html 
           }else if(json.error == false){
               console.log('ERROR : ',json.error);
               document.getElementById('btn_modalRequestClose').click();
               document.getElementById('btn_modalSuccess').click();
               document.getElementById('success').innerHTML = json.success 
                  
             }
                
         }
          else if(http.status != 200){
              
          }
        }
     http.send(formData);
    
   }